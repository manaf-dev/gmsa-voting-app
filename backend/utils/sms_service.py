"""
SMS Service for GMSA Voting System using mnotify API

This service handles all SMS communications including:
- Welcome messages for new users (bulk registration)
- Password reset notifications
- Voting reminders
- Election notifications
"""

import requests
import logging
from django.conf import settings
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SMSService:
    """SMS service using mnotify API"""

    def __init__(self):
        self.api_key = getattr(settings, "MNOTIFY_API_KEY", None)
        self.sender_id = getattr(settings, "MNOTIFY_SENDER_ID", "GMSA")
        self.base_url = getattr(
            settings, "MNOTIFY_BASE_URL", "https://api.mnotify.com/api"
        )

        if not self.api_key:
            logger.error("MNOTIFY_API_KEY not configured in settings")
            raise ValueError("MNOTIFY_API_KEY is required for SMS service")

    def send_single_sms(self, phone_number: str, message: str) -> Dict:
        """
        Send SMS to a single recipient

        Args:
            phone_number: Recipient's phone number (with country code)
            message: SMS message content

        Returns:
            dict: API response with status and message_id
        """
        # Clean phone number (remove spaces, ensure format)
        phone_number = self._clean_phone_number(phone_number)

        if not phone_number:
            return {"success": False, "error": "Invalid phone number"}

        url = f"{self.base_url}/sms/quick?key={self.api_key}"

        payload = {
            "recipient[]": [phone_number],
            "sender": self.sender_id,
            "message": message,
            "is_schedule": False,
            "schedule_date": "",
        }

        try:
            response = requests.post(url, data=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            # mnotify response format: {"status": "success", "code": "2000", "message": "messages sent successfully"}
            if result.get("code") == "2000":
                logger.info(f"SMS sent successfully to {phone_number}")
                return {
                    "success": True,
                    "message_id": result.get("summary", {}).get("_id"),
                    "response": result,
                }
            else:
                logger.error(f"SMS failed to {phone_number}: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "response": result,
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"SMS service error for {phone_number}: {str(e)}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {phone_number}: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def send_bulk_sms(self, recipients: List[Dict[str, str]]) -> Dict:
        """
        Send SMS to multiple recipients

        Args:
            recipients: List of dicts with 'phone' and 'message' keys

        Returns:
            dict: Summary of results
        """
        results = {"total": len(recipients), "success": 0, "failed": 0, "results": []}

        for recipient in recipients:
            phone = recipient.get("phone")
            message = recipient.get("message")

            if not phone or not message:
                results["failed"] += 1
                results["results"].append(
                    {
                        "phone": phone,
                        "success": False,
                        "error": "Missing phone or message",
                    }
                )
                continue

            result = self.send_single_sms(phone, message)

            if result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1

            results["results"].append(
                {
                    "phone": phone,
                    "success": result["success"],
                    "error": result.get("error"),
                    "message_id": result.get("message_id"),
                }
            )

        logger.info(
            f"Bulk SMS completed: {results['success']}/{results['total']} successful"
        )
        return results

    def _clean_phone_number(self, phone_number: str) -> Optional[str]:
        """
        Clean and format phone number for Ghana (mnotify accepts local format)

        Args:
            phone_number: Raw phone number

        Returns:
            str: Cleaned phone number in local format (0XXXXXXXXX) or None if invalid
        """
        if not phone_number:
            return None

        # Remove all non-digit characters
        digits = "".join(filter(str.isdigit, phone_number))

        if not digits:
            return None

        # Handle Ghana phone numbers - convert to local format (0XXXXXXXXX)
        if digits.startswith("233"):
            # Has country code (233241234567 -> 0241234567)
            if len(digits) == 12:
                return "0" + digits[3:]
        elif digits.startswith("0"):
            # Already in local format (0241234567)
            if len(digits) == 10:
                return digits
        elif len(digits) == 9:
            # Missing leading 0 (241234567 -> 0241234567)
            return "0" + digits

        # Return as-is if it looks valid but doesn't match patterns
        if 10 <= len(digits) <= 15:
            # If it's an international format without 233, add 0 prefix
            if len(digits) == 9:
                return "0" + digits
            return digits

        logger.warning(f"Invalid phone number format: {phone_number}")
        return None


class SMSMessageTemplates:
    """Templates for different types of SMS messages"""

    @staticmethod
    def welcome_new_user(user_data: Dict) -> str:
        """
        Welcome message for newly registered users

        Args:
            user_data: Dict with username, password, student_id, first_name
        """
        return f"""Assalamu Alaikum, You have been registered as a voter in the upcoming GMSA Election.
Below are you account details:
Username: {user_data['username']}
Password: {user_data['password']}

Login at: {settings.FRONTEND_URL}/login

Please change your password after first login.

- GMSA Electoral Commission"""

    @staticmethod
    def password_reset(user_data: Dict) -> str:
        """
        Password reset notification

        Args:
            user_data: Dict with username, new_password, first_name
        """
        return f"""GMSA Password Reset

Hello {user_data.get('first_name', 'Student')},

Your password has been reset by EC:
Username: {user_data['username']}
New Password: {user_data['new_password']}

Login at: {settings.FRONTEND_URL}/login
Please change this password immediately.

- GMSA Electoral Commission"""

    @staticmethod
    def voting_reminder(election_data: Dict, user_data: Dict) -> str:
        """
        Voting reminder message

        Args:
            election_data: Dict with title, end_date
            user_data: Dict with first_name
        """
        return f"""GMSA Voting Reminder

Hello {user_data.get('first_name', 'Student')},

Election: {election_data['title']}
Voting ends: {election_data['end_date']}

You haven't voted yet. Cast your vote now!
Login: {settings.FRONTEND_URL}/login

- GMSA Electoral Commission"""

    @staticmethod
    def results_published(election_data: Dict, user_data: Dict) -> str:
        """
        Results published notification

        Args:
            election_data: Dict with title, results_url
            user_data: Dict with first_name
        """
        return f"""GMSA Election Results Published

Hello {user_data.get('first_name', 'Student')},

Official results for '{election_data.get('title')}' are now available.
View results: {election_data.get('results_url')}

- GMSA Electoral Commission"""

    @staticmethod
    def dues_payment_reminder(user_data: Dict, academic_year: str) -> str:
        """
        Dues payment reminder

        Args:
            user_data: Dict with first_name
            academic_year: Academic year string
        """
        return f"""GMSA Dues Reminder

Hello {user_data.get('first_name', 'Student')},

Your dues for {academic_year} are unpaid.
Pay now to be eligible for voting.

Login: {settings.FRONTEND_URL}/login

- GMSA Electoral Commission"""


def get_sms_service() -> SMSService:
    """Factory function to get SMS service instance"""
    return SMSService()


# Convenience functions for common SMS operations
def send_welcome_sms(user, password: str, async_send: bool = True) -> Dict:
    """
    Send welcome SMS to new user

    Args:
        user: User instance
        username: Username for login
        password: Generated password
        async_send: Whether to send via Celery task (default True)
    """

    user_data = {
        "username": user.username,
        "password": password,
        "student_id": user.student_id,
        "first_name": user.first_name or user.username,
    }

    if async_send:
        # Import here to avoid circular imports
        from utils.tasks import send_welcome_sms_task

        task = send_welcome_sms_task.delay(user.id, user_data)
        return {
            "success": True,
            "task_id": task.id,
            "message": "SMS queued for sending",
        }

    # Synchronous sending
    sms_service = get_sms_service()

    message = SMSMessageTemplates.welcome_new_user(user_data)
    return sms_service.send_single_sms(user.phone_number, message)


def send_password_reset_sms(user, new_password: str, async_send: bool = True) -> Dict:
    """
    Send password reset SMS

    Args:
        user: User instance
        new_password: New password
        async_send: Whether to send via Celery task (default True)
    """
    if async_send:
        # Import here to avoid circular imports
        from utils.tasks import send_password_reset_sms_task

        task = send_password_reset_sms_task.delay(user.id, new_password)
        return {
            "success": True,
            "task_id": task.id,
            "message": "SMS queued for sending",
        }

    # Synchronous sending
    sms_service = get_sms_service()

    user_data = {
        "username": user.username,
        "new_password": new_password,
        "first_name": user.first_name or user.username,
    }

    message = SMSMessageTemplates.password_reset(user_data)
    return sms_service.send_single_sms(user.phone_number, message)


def send_voting_reminder_sms(user, election, async_send: bool = True) -> Dict:
    """
    Send voting reminder SMS

    Args:
        user: User instance
        election: Election instance
        async_send: Whether to send via Celery task (default True)
    """
    if async_send:
        # Import here to avoid circular imports
        from utils.tasks import send_voting_reminder_task

        task = send_voting_reminder_task.delay(user.id, election.id)
        return {
            "success": True,
            "task_id": task.id,
            "message": "SMS queued for sending",
        }

    # Synchronous sending
    sms_service = get_sms_service()

    user_data = {"first_name": user.first_name or user.username}

    election_data = {
        "title": election.title,
        "end_date": election.end_date.strftime("%Y-%m-%d %H:%M"),
    }

    message = SMSMessageTemplates.voting_reminder(election_data, user_data)
    return sms_service.send_single_sms(user.phone_number, message)
