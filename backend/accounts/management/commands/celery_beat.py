"""
Django management command to start Celery Beat scheduler for BESA Voting System

Usage:
    python manage.py celery_beat
    python manage.py celery_beat --loglevel debug
"""

from django.core.management.base import BaseCommand
import subprocess
import os


class Command(BaseCommand):
    help = "Start Celery Beat scheduler for periodic tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--loglevel",
            type=str,
            default="info",
            choices=["debug", "info", "warning", "error", "critical"],
            help="Logging level (default: info)",
        )

    def handle(self, *args, **options):
        loglevel = options["loglevel"]

        # Build celery beat command
        cmd = [
            "celery",
            "-A",
            "voting_system",
            "beat",
            "--loglevel",
            loglevel,
        ]

        self.stdout.write(self.style.SUCCESS("Starting Celery Beat scheduler..."))
        self.stdout.write(f"Log level: {loglevel}")

        try:
            # Set environment
            env = os.environ.copy()
            env["DJANGO_SETTINGS_MODULE"] = "voting_system.settings"

            # Run celery beat
            result = subprocess.run(cmd, env=env)

            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS("Celery Beat started successfully")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Celery Beat failed with return code {result.returncode}"
                    )
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    "Celery not found. Make sure it's installed: pip install celery"
                )
            )
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nCelery Beat stopped by user"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error starting Celery Beat: {str(e)}"))
