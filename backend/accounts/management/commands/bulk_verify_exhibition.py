from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from accounts.models import ExhibitionEntry, User
from utils.helpers import _generate_password, _generate_username
from utils.sms_service import send_welcome_sms


class Command(BaseCommand):
    help = 'Bulk verify exhibition entries and create user accounts with SMS (CLI fallback)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of entries to process (for testing)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        
        # Get unverified entries
        unverified_entries = ExhibitionEntry.objects.filter(is_verified=False)
        
        if limit:
            unverified_entries = unverified_entries[:limit]
            
        total_count = unverified_entries.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING('No unverified exhibition entries found.')
            )
            return
        
        self.stdout.write(f'Found {total_count} unverified entries to process.')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            for entry in unverified_entries:
                self.stdout.write(f'Would process: {entry.first_name} {entry.last_name} ({entry.phone_number})')
            return
        
        # Confirm action
        confirm = input(f'Process {total_count} entries? (y/N): ')
        if confirm.lower() != 'y':
            self.stdout.write('Operation cancelled.')
            return
        
        verified_count = 0
        promoted_count = 0
        sms_sent_count = 0
        errors = []
        
        self.stdout.write('Starting bulk verification...')
        
        with transaction.atomic():
            for i, entry in enumerate(unverified_entries, 1):
                try:
                    self.stdout.write(f'Processing {i}/{total_count}: {entry.first_name} {entry.last_name}')
                    
                    # Mark as verified
                    entry.is_verified = True
                    entry.verified_at = timezone.now()
                    # Note: CLI doesn't have a user context, so verified_by will be None
                    verified_count += 1
                    
                    # Check if user already exists with this phone
                    if User.objects.filter(phone_number=entry.phone_number).exists():
                        entry.save()
                        self.stdout.write(f'  ⚠️  User with phone {entry.phone_number} already exists, skipping user creation')
                        continue
                    
                    # Generate student ID if missing
                    sid = entry.student_id or f"EXH{User.objects.count()+1:05d}"
                    if User.objects.filter(student_id=sid).exists():
                        suffix = User.objects.count() + 1
                        while User.objects.filter(student_id=f"{sid}-{suffix}").exists():
                            suffix += 1
                        sid = f"{sid}-{suffix}"
                    
                    # Generate username
                    username = _generate_username(entry.first_name, entry.last_name, sid)
                    raw_password = _generate_password()
                    
                    # Create user account
                    user = User(
                        username=username,
                        student_id=sid,
                        first_name=entry.first_name,
                        last_name=entry.last_name,
                        phone_number=entry.phone_number,
                        program=entry.program,
                        year_of_study=entry.year_of_study,
                        hall=entry.hall or ''
                    )
                    user.set_password(raw_password)
                    user.can_vote = True
                    user.changed_password = False
                    user.save()
                    
                    # Link to exhibition entry
                    entry.user = user
                    entry.save()
                    promoted_count += 1
                    
                    self.stdout.write(f'  ✅ Created user: {username} (ID: {sid})')
                    
                    # Send SMS
                    if user.phone_number:
                        try:
                            send_welcome_sms(user, raw_password, async_send=True)
                            sms_sent_count += 1
                            self.stdout.write(f'  📱 SMS sent to {user.phone_number}')
                        except Exception as e:
                            error_msg = f"SMS failed for {user.phone_number}: {str(e)}"
                            errors.append(error_msg)
                            self.stdout.write(f'  ❌ {error_msg}')
                
                except Exception as e:
                    error_msg = f"Failed to process entry {entry.id}: {str(e)}"
                    errors.append(error_msg)
                    self.stdout.write(f'  ❌ {error_msg}')
                    continue
        
        # Final summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('BULK VERIFICATION COMPLETED'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'📊 Entries verified: {verified_count}')
        self.stdout.write(f'👤 User accounts created: {promoted_count}')
        self.stdout.write(f'📱 SMS notifications sent: {sms_sent_count}')
        
        if errors:
            self.stdout.write(self.style.WARNING(f'⚠️  Errors encountered: {len(errors)}'))
            for error in errors[:5]:  # Show first 5 errors
                self.stdout.write(self.style.ERROR(f'   • {error}'))
            if len(errors) > 5:
                self.stdout.write(self.style.WARNING(f'   ... and {len(errors) - 5} more errors'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ No errors encountered'))
