import csv
from django.core.management.base import BaseCommand, CommandError
from accounts.models import ExhibitionEntry, User
from django.utils import timezone

REQUIRED_HEADERS = {"phone_number", "first_name", "last_name"}
OPTIONAL_HEADERS = {"student_id", "program", "year_of_study", "hall"}
ALL_HEADERS = REQUIRED_HEADERS | OPTIONAL_HEADERS


def normalize_phone(raw: str) -> str | None:
    digits = ''.join(ch for ch in raw if ch.isdigit())
    if digits.startswith('233') and len(digits) >= 12:
        digits = '0' + digits[3:3+9]
    elif len(digits) == 9:
        digits = '0' + digits
    if len(digits) != 10 or not digits.startswith('0'):
        return None
    return digits


class Command(BaseCommand):
    help = "Load valid users from a CSV into the exhibition register (ExhibitionEntry)."

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Path to CSV file containing register rows')
        parser.add_argument('--source', default='imported', help='Source label (default: imported)')
        parser.add_argument('--mark-verified', action='store_true', help='Mark imported entries as verified')
        parser.add_argument('--dry-run', action='store_true', help='Dry run without writing to DB')

    def handle(self, *args, **options):
        path = options['csv_path']
        source = options['source']
        mark_verified = options['mark_verified']
        dry = options['dry_run']

        try:
            f = open(path, 'r', newline='', encoding='utf-8-sig')
        except OSError as e:
            raise CommandError(f"Cannot open file: {e}")

        with f:
            reader = csv.DictReader(f)
            headers = set([h.strip() for h in reader.fieldnames or []])
            missing = REQUIRED_HEADERS - headers
            if missing:
                raise CommandError(f"Missing required headers: {', '.join(sorted(missing))}")

            imported = 0
            skipped_phone = 0
            skipped_duplicate = 0
            existing_user_conflict = 0

            for row in reader:
                phone_number = normalize_phone(row.get('phone_number', ''))
                if not phone_number:
                    skipped_phone += 1
                    continue
                if ExhibitionEntry.objects.filter(phone_number=phone_number).exists():
                    skipped_duplicate += 1
                    continue
                if User.objects.filter(phone_number=phone_number).exists():
                    existing_user_conflict += 1
                    continue
                data = {
                    'phone_number': phone_number,
                    'first_name': (row.get('first_name') or '').strip().title(),
                    'last_name': (row.get('last_name') or '').strip().title(),
                    'student_id': (row.get('student_id') or '').strip(),
                    'program': (row.get('program') or '').strip(),
                    'year_of_study': (row.get('year_of_study') or '').strip(),
                    'hall': (row.get('hall') or '').strip() or None,
                    'source': source,
                }
                if mark_verified:
                    data['is_verified'] = True
                    data['verified_at'] = timezone.now()
                if dry:
                    imported += 1
                else:
                    ExhibitionEntry.objects.create(**data)
                    imported += 1

        self.stdout.write(self.style.SUCCESS(
            f"Imported {imported} entries (duplicates: {skipped_duplicate}, bad phone: {skipped_phone}, existing users: {existing_user_conflict})"
        ))
        if dry:
            self.stdout.write(self.style.WARNING('Dry run mode - no database changes committed.'))
