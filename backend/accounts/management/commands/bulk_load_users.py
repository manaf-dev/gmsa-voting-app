"""
Django management command for bulk loading users from CSV file

This command allows you to:
1. Load users from a CSV file
2. Generate usernames and passwords if not provided
3. Send welcome SMS to all new users via Celery
4. Update existing users if they already exist

Usage:
    python manage.py bulk_load_users path/to/users.csv --send-sms
    python manage.py bulk_load_users users.csv --dry-run
    python manage.py bulk_load_users users.csv --send-sms --update-existing
"""

import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import AcademicYear
from utils.sms_service import send_welcome_sms
from utils.helpers import _generate_password

User = get_user_model()


class Command(BaseCommand):
    help = "Bulk load users from CSV file with optional SMS notifications"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--send-sms",
            action="store_true",
            help="Send welcome SMS to new users via Celery",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be created without making changes",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing users if they already exist",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        send_sms = options["send_sms"]
        dry_run = options["dry_run"]
        update_existing = options["update_existing"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 DRY RUN MODE - No actual changes will be made")
            )

        try:
            with open(csv_file, "r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)

                # Validate CSV headers
                required_fields = [
                    "student_id",
                    "first_name",
                    "last_name",
                    "phone_number",
                ]
                missing_fields = [
                    field
                    for field in required_fields
                    if field not in csv_reader.fieldnames
                ]

                if missing_fields:
                    raise CommandError(
                        f"Missing required CSV fields: {', '.join(missing_fields)}"
                    )

                users_data = list(csv_reader)

        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {str(e)}")

        if not users_data:
            self.stdout.write(self.style.WARNING("No data found in CSV file"))
            return

        self.stdout.write(f"📊 Processing {len(users_data)} rows from CSV...\n")

        # Process users
        stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "sms_sent": 0,
            "sms_failed": 0,
        }

        users_to_send_sms = []  # Store users for SMS sending

        # Get or create current academic year
        try:
            current_year = AcademicYear.objects.get(is_current=True)
        except AcademicYear.DoesNotExist:
            # Create a default academic year if none exists
            from datetime import date

            year = date.today().year
            current_year = AcademicYear.objects.create(
                year=f"{year}/{year+1}",
                is_current=True,
                start_date=date(year, 9, 1),  # September 1st
                end_date=date(year + 1, 8, 31),  # August 31st next year
                dues_amount=30.00,
            )

        with transaction.atomic():
            for row_num, row in enumerate(
                users_data, start=2
            ):  # Start at 2 for Excel row numbering
                try:
                    # Extract and clean data
                    student_id = row.get("student_id", "").strip()
                    first_name = row.get("first_name", "").strip()
                    last_name = row.get("last_name", "").strip()
                    phone_number = row.get("phone_number", "").strip()
                    email = row.get("email", "").strip()
                    username = row.get("username", "").strip()
                    password = row.get("password", "").strip()
                    program = row.get("program", "").strip()
                    year_of_study = row.get("year_of_study", "").strip()

                    # Validate required fields
                    if not all([student_id, first_name, last_name, phone_number]):
                        self.stdout.write(
                            self.style.ERROR(
                                f"❌ Row {row_num}: Missing required fields"
                            )
                        )
                        stats["errors"] += 1
                        continue

                    # Generate username if not provided
                    if not username:
                        username = self._generate_username(
                            first_name, last_name, student_id
                        )

                    # Generate password if not provided
                    if not password:
                        password = _generate_password()

                    # Generate email if not provided
                    if not email:
                        email = f"{username}@aamustedgmsa.org"

                    # Check if user exists
                    user_exists = User.objects.filter(student_id=student_id).exists()

                    if user_exists and not update_existing:
                        self.stdout.write(
                            f"⚠️  Row {row_num}: User {student_id} already exists (skipped)"
                        )
                        stats["skipped"] += 1
                        continue

                    if dry_run:
                        action = "UPDATE" if user_exists else "CREATE"
                        self.stdout.write(
                            f'🔍 Row {row_num}: Would {action} user {student_id} ({username}) - SMS: {"Yes" if send_sms else "No"}'
                        )
                        if user_exists:
                            stats["updated"] += 1
                        else:
                            stats["created"] += 1
                        continue

                    # Create or update user
                    if user_exists:
                        user = User.objects.get(student_id=student_id)
                        user.first_name = first_name
                        user.last_name = last_name
                        user.phone_number = phone_number
                        user.email = email
                        user.username = username
                        user.save()

                        self.stdout.write(
                            f"🔄 Row {row_num}: Updated user {student_id} ({username})"
                        )
                        stats["updated"] += 1
                    else:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            student_id=student_id,
                            first_name=first_name,
                            last_name=last_name,
                            phone_number=phone_number,
                            program=program,
                            year_of_study=year_of_study,
                        )

                        self.stdout.write(
                            f"✅ Row {row_num}: Created user {student_id} ({username})"
                        )
                        stats["created"] += 1

                        # Add to SMS queue if creating new user
                        if send_sms and user.phone_number:
                            users_to_send_sms.append((user, username, password))

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Row {row_num}: Error processing row - {str(e)}"
                        )
                    )
                    stats["errors"] += 1

        # Send SMS notifications if not dry run
        if send_sms and users_to_send_sms and not dry_run:
            self.stdout.write(
                f"\n📱 Sending welcome SMS to {len(users_to_send_sms)} users..."
            )

            for user, username, password in users_to_send_sms:
                try:
                    result = send_welcome_sms(user, password, async_send=True)
                    if result["success"]:
                        stats["sms_sent"] += 1
                        self.stdout.write(
                            f"✓ SMS queued for {user.student_id} ({user.phone_number})"
                        )
                    else:
                        stats["sms_failed"] += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'✗ SMS failed for {user.student_id}: {result.get("error")}'
                            )
                        )
                except Exception as e:
                    stats["sms_failed"] += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"✗ SMS error for {user.student_id}: {str(e)}"
                        )
                    )

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("📊 BULK LOAD SUMMARY"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"Total rows processed: {len(users_data)}")
        self.stdout.write(f'Users created: {stats["created"]}')
        self.stdout.write(f'Users updated: {stats["updated"]}')
        self.stdout.write(f'Users skipped: {stats["skipped"]}')
        self.stdout.write(f'Errors: {stats["errors"]}')

        if send_sms and not dry_run:
            self.stdout.write(f'SMS queued: {stats["sms_sent"]}')
            self.stdout.write(f'SMS failed: {stats["sms_failed"]}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n🔍 This was a dry run - no actual changes were made"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✅ Bulk load completed successfully!")
            )

    def _generate_username(
        self, first_name: str, last_name: str, student_id: str
    ) -> str:
        """Generate username from first name, last name, and student ID"""
        # Clean names
        first_clean = first_name.capitalize().replace(" ", "")
        last_clean = last_name.capitalize().replace(" ", "")

        # Try different username patterns
        patterns = [
            f"{first_clean}_{last_clean[:2]}",
            f"{first_clean}_{last_clean[:3]}",
            f"{first_clean}.{last_clean[:2]}",
            f"{first_clean}{last_clean[:3]}",
            f"user{student_id}",
        ]

        for pattern in patterns:
            if not User.objects.filter(username=pattern).exists():
                return pattern

        # If all patterns exist, append a number
        base_username = patterns[0]
        counter = 1
        while User.objects.filter(username=f"{base_username}{counter}").exists():
            counter += 1

        return f"{base_username}{counter}"
