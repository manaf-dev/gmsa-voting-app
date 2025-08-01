"""
Celery configuration for GMSA Voting System

This module configures Celery for handling async SMS tasks including:
- Welcome messages for new users (bulk registration)
- Password reset notifications
- Voting reminders
- Election notifications
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voting_system.settings")

app = Celery("voting_system")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Explicitly set the broker URL to ensure Redis is used
# app.conf.broker_url = "redis://localhost:6379/0"
# app.conf.result_backend = "redis://localhost:6379/0"

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Send voting reminders daily at 9 AM
    "send-daily-voting-reminders": {
        "task": "utils.tasks.send_daily_voting_reminders",
        "schedule": 60.0 * 60.0 * 24.0,  # Every 24 hours
        "options": {"queue": "sms_queue"},
    },
}

# Task routing
app.conf.task_routes = {
    "utils.tasks.send_single_sms_task": {"queue": "sms_queue"},
    "utils.tasks.send_bulk_sms_task": {"queue": "sms_queue"},
    "utils.tasks.send_welcome_sms_task": {"queue": "sms_queue"},
    "utils.tasks.send_password_reset_sms_task": {"queue": "sms_queue"},
    "utils.tasks.send_voting_reminder_task": {"queue": "sms_queue"},
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
