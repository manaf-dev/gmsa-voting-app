"""
Celery tasks for GMSA Voting System

This module contains all async tasks including:
- SMS sending tasks
- Scheduled reminder tasks
- Election notification tasks
"""

import logging
from datetime import timedelta
from typing import List, Dict, Any
import uuid
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from utils.sms_service import (
    SMSService,
    SMSMessageTemplates,
)

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_single_sms_task(self, phone_number: str, message: str) -> Dict[str, Any]:
    """
    Send SMS to a single recipient (async)

    Args:
        phone_number: Recipient's phone number
        message: SMS message content

    Returns:
        dict: Result of SMS sending
    """
    try:
        sms_service = SMSService()
        result = sms_service.send_single_sms(phone_number, message)

        if not result.get("success"):
            logger.error(f"SMS failed to {phone_number}: {result.get('error')}")
            # Retry failed SMS
            raise self.retry(countdown=60, exc=Exception(result.get("error")))

        logger.info(f"SMS sent successfully to {phone_number}")
        return result

    except Exception as exc:
        logger.error(f"SMS task failed for {phone_number}: {str(exc)}")
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=2)
def send_bulk_sms_task(self, recipients: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Send SMS to multiple recipients (async)

    Args:
        recipients: List of dicts with 'phone' and 'message' keys

    Returns:
        dict: Summary of bulk SMS results
    """
    try:
        sms_service = SMSService()
        result = sms_service.send_bulk_sms(recipients)

        logger.info(
            f"Bulk SMS completed: {result['success']}/{result['total']} successful"
        )
        return result

    except Exception as exc:
        logger.error(f"Bulk SMS task failed: {str(exc)}")
        raise self.retry(countdown=120, exc=exc)


@shared_task(bind=True, max_retries=3)
def send_welcome_sms_task(self, user_id: str, user_data: dict) -> Dict[str, Any]:
    """
    Send welcome SMS to new user (async)

    Args:
        user_id: User ID
        username: User's username
        password: Generated password

    Returns:
        dict: Result of SMS sending
    """
    try:
        user = User.objects.get(id=user_id)

        message = SMSMessageTemplates.welcome_new_user(user_data)
        sms_service = SMSService()
        result = sms_service.send_single_sms(user.phone_number, message)

        if not result.get("success"):
            logger.error(
                f"Welcome SMS failed for user {user_id}: {result.get('error')}"
            )
            raise self.retry(countdown=60, exc=Exception(result.get("error")))

        logger.info(f"Welcome SMS sent to user {user_id}")
        return result

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for welcome SMS")
        return {"success": False, "error": "User not found"}
    except Exception as exc:
        logger.error(f"Welcome SMS task failed for user {user_id}: {str(exc)}")
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def send_password_reset_sms_task(
    self, user_id: int, new_password: str
) -> Dict[str, Any]:
    """
    Send password reset SMS (async)

    Args:
        user_id: User ID
        new_password: New password

    Returns:
        dict: Result of SMS sending
    """
    try:
        user = User.objects.get(id=user_id)

        user_data = {
            "username": user.username,
            "new_password": new_password,
            "first_name": user.first_name or user.username,
        }

        message = SMSMessageTemplates.password_reset(user_data)
        sms_service = SMSService()
        result = sms_service.send_single_sms(user.phone_number, message)

        if not result.get("success"):
            logger.error(
                f"Password reset SMS failed for user {user_id}: {result.get('error')}"
            )
            raise self.retry(countdown=60, exc=Exception(result.get("error")))

        logger.info(f"Password reset SMS sent to user {user_id}")
        return result

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for password reset SMS")
        return {"success": False, "error": "User not found"}
    except Exception as exc:
        logger.error(f"Password reset SMS task failed for user {user_id}: {str(exc)}")
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def send_voting_reminder_task(self, user_id: int, election_id: int) -> Dict[str, Any]:
    """
    Send voting reminder SMS (async)

    Args:
        user_id: User ID
        election_id: Election ID

    Returns:
        dict: Result of SMS sending
    """
    try:
        from elections.models import Election

        user = User.objects.get(id=user_id)
        election = Election.objects.get(id=election_id)

        user_data = {"first_name": user.first_name or user.username}

        election_data = {
            "title": election.title,
            "end_date": election.end_date.strftime("%Y-%m-%d %H:%M"),
        }

        message = SMSMessageTemplates.voting_reminder(election_data, user_data)
        sms_service = SMSService()
        result = sms_service.send_single_sms(user.phone_number, message)

        if not result.get("success"):
            logger.error(
                f"Voting reminder SMS failed for user {user_id}: {result.get('error')}"
            )
            raise self.retry(countdown=60, exc=Exception(result.get("error")))

        logger.info(
            f"Voting reminder SMS sent to user {user_id} for election {election_id}"
        )
        return result

    except (User.DoesNotExist, Exception) as exc:
        if "DoesNotExist" in str(type(exc)):
            logger.error(f"User {user_id} or Election {election_id} not found")
            return {"success": False, "error": "User or Election not found"}

        logger.error(f"Voting reminder SMS task failed: {str(exc)}")
        raise self.retry(countdown=60, exc=exc)


# Periodic tasks for scheduled reminders
@shared_task(bind=True)
def send_daily_voting_reminders(self) -> Dict[str, Any]:
    """
    Send daily voting reminders to users who haven't voted in active elections
    Runs every day at 9 AM
    """
    try:
        from elections.models import Election, Vote

        # Get active elections (ongoing voting)
        now = timezone.now()
        active_elections = Election.objects.filter(
            start_date__lte=now, end_date__gte=now, is_active=True
        )

        if not active_elections.exists():
            logger.info("No active elections found for voting reminders")
            return {"success": True, "message": "No active elections"}

        total_reminders = 0

        for election in active_elections:
            # Get users who haven't voted in this election
            voted_user_ids = Vote.objects.filter(election=election).values_list(
                "voter_id", flat=True
            )

            eligible_users = User.objects.filter(
                is_active=True,
                phone_number__isnull=False,
            ).exclude(id__in=voted_user_ids)

            # Send reminders in batches to avoid overwhelming the system
            batch_size = 50
            for i in range(0, eligible_users.count(), batch_size):
                batch_users = eligible_users[i : i + batch_size]

                for user in batch_users:
                    # Schedule individual SMS tasks
                    send_voting_reminder_task.delay(user.id, election.id)
                    total_reminders += 1

        logger.info(f"Scheduled {total_reminders} voting reminder SMS tasks")
        return {"success": True, "reminders_scheduled": total_reminders}

    except Exception as exc:
        logger.error(f"Daily voting reminders task failed: {str(exc)}")
        return {"success": False, "error": str(exc)}


# Periodic task to manage election lifecycle based on start/end times
@shared_task(bind=True)
def update_election_statuses(self) -> Dict[str, Any]:
    """
    Activate elections when start time is reached and mark as completed when end time passes.
    Runs periodically via Celery Beat.
    """
    try:
        from elections.models import Election

        now = timezone.now()

        # Activate elections that are scheduled to start
        to_activate = Election.objects.filter(status="upcoming", start_date__lte=now)
        activated = to_activate.update(status="active") if to_activate.exists() else 0

        # Complete elections that have ended
        to_complete = Election.objects.filter(status="active", end_date__lt=now)
        completed = to_complete.update(status="completed") if to_complete.exists() else 0

        if activated or completed:
            logger.info(
                f"Election status update: activated={activated}, completed={completed}"
            )

        return {"success": True, "activated": activated, "completed": completed}

    except Exception as exc:
        logger.error(f"update_election_statuses failed: {str(exc)}")
        return {"success": False, "error": str(exc)}


@shared_task(bind=True, max_retries=3)
def send_bulk_results_published_sms_task(self, election_id: str, user_ids: list) -> Dict[str, Any]:
    """Send 'results published' SMS to a list of users."""
    try:
        from elections.models import Election
        election = Election.objects.get(id=election_id)
        users = User.objects.filter(id__in=user_ids, is_active=True)
        recipients = []
        for u in users:
            if not u.phone_number:
                continue
            message = SMSMessageTemplates.results_published({
                "title": election.title,
                "results_url": f"{getattr(settings, 'FRONTEND_URL', '').rstrip('/')}/elections/{election.id}/results",
            }, {
                "first_name": u.first_name or u.username,
            })
            recipients.append({"phone": u.phone_number, "message": message})

        if not recipients:
            return {"success": True, "total": 0}

        sms_service = SMSService()
        result = sms_service.send_bulk_sms(recipients)
        return result
    except Exception as exc:
        logger.error(f"send_bulk_results_published_sms_task failed: {str(exc)}")
        raise self.retry(countdown=120, exc=exc)
