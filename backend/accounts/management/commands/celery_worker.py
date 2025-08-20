"""
Django management command to start Celery worker for BESA Voting System

Usage:
    python manage.py celery_worker
    python manage.py celery_worker --queue sms_queue
    python manage.py celery_worker --concurrency 8
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os


class Command(BaseCommand):
    help = "Start Celery worker for async task processing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue",
            type=str,
            default="default,sms_queue",
            help="Comma-separated list of queues to process (default: default,sms_queue)",
        )
        parser.add_argument(
            "--concurrency",
            type=int,
            default=getattr(settings, "CELERY_WORKER_CONCURRENCY", 4),
            help="Number of concurrent worker processes (default: 4)",
        )
        parser.add_argument(
            "--loglevel",
            type=str,
            default="info",
            choices=["debug", "info", "warning", "error", "critical"],
            help="Logging level (default: info)",
        )

    def handle(self, *args, **options):
        queue = options["queue"]
        concurrency = options["concurrency"]
        loglevel = options["loglevel"]

        # Build celery worker command
        cmd = [
            "celery",
            "-A",
            "voting_system",
            "worker",
            "--loglevel",
            loglevel,
            "--concurrency",
            str(concurrency),
            "--queues",
            queue,
        ]

        self.stdout.write(self.style.SUCCESS("Starting Celery worker..."))
        self.stdout.write(f"Queues: {queue}")
        self.stdout.write(f"Concurrency: {concurrency}")
        self.stdout.write(f"Log level: {loglevel}")

        try:
            # Set environment
            env = os.environ.copy()
            env["DJANGO_SETTINGS_MODULE"] = "voting_system.settings"

            # Run celery worker
            result = subprocess.run(cmd, env=env)

            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS("Celery worker started successfully")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Celery worker failed with return code {result.returncode}"
                    )
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    "Celery not found. Make sure it's installed: pip install celery"
                )
            )
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nCelery worker stopped by user"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error starting Celery worker: {str(e)}")
            )
