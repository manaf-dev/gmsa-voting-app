from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, AcademicYear, ExhibitionEntry
from utils.helpers import _generate_password, _generate_username
from utils.sms_service import send_welcome_sms


class UnverifiedEntriesFilter(admin.SimpleListFilter):
    title = 'Verification Status'
    parameter_name = 'verification_status'

    def lookups(self, request, model_admin):
        return (
            ('unverified_only', 'Unverified Only (Ready for Bulk)'),
            ('verified_no_account', 'Verified but No User Account'),
            ('complete', 'Complete (Verified + User Account)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'unverified_only':
            return queryset.filter(is_verified=False)
        elif self.value() == 'verified_no_account':
            return queryset.filter(is_verified=True, user__isnull=True)
        elif self.value() == 'complete':
            return queryset.filter(is_verified=True, user__isnull=False)
        return queryset


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "student_id",
        "year_of_study",
        "is_ec_member",
        "date_joined",
    )
    list_filter = ("year_of_study", "is_ec_member", "admission_year")
    search_fields = ("username", "email", "student_id", "first_name", "last_name")

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "BESA Information",
            {
                "fields": (
                    "student_id",
                    "phone_number",
                    "year_of_study",
                    "program",
                    "admission_year",
                )
            },
        ),
        ("Permissions", {"fields": ("is_ec_member", "changed_password")}),
    )

    actions = ["promote_to_next_level", "mark_as_graduate", "mark_as_alumni"]

    def promote_to_next_level(self, request, queryset):
        """Promote students to next level"""
        level_progression = {
            "100": "200",
            "200": "300",
            "300": "400",
            "400": "graduate",
        }

        updated = 0
        for user in queryset:
            if user.year_of_study in level_progression:
                user.year_of_study = level_progression[user.year_of_study]
                user.save()
                updated += 1

        self.message_user(request, f"Promoted {updated} students to next level.")

    promote_to_next_level.short_description = "Promote selected students to next level"

    def mark_as_graduate(self, request, queryset):
        queryset.update(year_of_study="graduate")
        self.message_user(request, f"Marked {queryset.count()} users as graduates.")

    mark_as_graduate.short_description = "Mark selected users as graduates"

    def mark_as_alumni(self, request, queryset):
        queryset.update(year_of_study="alumni")
        self.message_user(request, f"Marked {queryset.count()} users as alumni.")

    mark_as_alumni.short_description = "Mark selected users as alumni"

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("year", "dues_amount", "is_current", "start_date", "end_date")
    list_filter = ("is_current",)
    search_fields = ("year",)

    actions = ["set_as_current_year"]

    def set_as_current_year(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "Please select only one academic year to set as current.",
                level="ERROR",
            )
            return

        # Set all years as not current first
        AcademicYear.objects.update(is_current=False)
        # Set selected year as current
        queryset.update(is_current=True)

        year = queryset.first()
        self.message_user(request, f"Set {year.year} as the current academic year.")

    set_as_current_year.short_description = "Set as current academic year"


@admin.register(ExhibitionEntry)
class ExhibitionEntryAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number', 'first_name', 'last_name', 'student_id', 'program', 
        'year_of_study', 'is_verified', 'has_user_account', 'source', 'verified_at'
    )
    list_filter = ('is_verified', 'source', 'year_of_study', 'program', 'verified_at')
    search_fields = ('phone_number', 'first_name', 'last_name', 'student_id')
    readonly_fields = ('verified_at', 'verified_by', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'verified_by')
    
    # Enhanced filters for bulk operations
    list_filter = (
        UnverifiedEntriesFilter,
        'is_verified', 
        'source', 
        'year_of_study', 
        'program',
        ('verified_at', admin.DateFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
    )
    
    def has_user_account(self, obj):
        return obj.user is not None
    has_user_account.boolean = True
    has_user_account.short_description = 'User Account'
    
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to the changelist"""
        extra_context = extra_context or {}
        
        # Get statistics
        total_entries = ExhibitionEntry.objects.count()
        unverified_count = ExhibitionEntry.objects.filter(is_verified=False).count()
        verified_no_account = ExhibitionEntry.objects.filter(is_verified=True, user__isnull=True).count()
        complete_count = ExhibitionEntry.objects.filter(is_verified=True, user__isnull=False).count()
        
        extra_context['summary_stats'] = {
            'total_entries': total_entries,
            'unverified_count': unverified_count,
            'verified_no_account': verified_no_account,
            'complete_count': complete_count,
        }
        
        return super().changelist_view(request, extra_context=extra_context)
    actions = ['mark_verified', 'promote_verified_entries', 'bulk_verify_and_promote_with_sms', 'select_all_unverified']
    
    def select_all_unverified(self, request, queryset):
        """Helper action to show count of unverified entries for selection"""
        unverified_count = ExhibitionEntry.objects.filter(is_verified=False).count()
        self.message_user(
            request, 
            f"Found {unverified_count} unverified entries. Use the 'Unverified Only' filter to see them, then select all for bulk processing.",
            level='info'
        )
    select_all_unverified.short_description = "ℹ️ Show unverified count (use filter to select)"

    def mark_verified(self, request, queryset):
        updated = queryset.filter(is_verified=False).update(
            is_verified=True, verified_at=timezone.now(), verified_by=request.user
        )
        self.message_user(request, f"Marked {updated} entries as verified.")
    mark_verified.short_description = "Mark selected entries as verified"

    def promote_verified_entries(self, request, queryset):
        promoted_count = 0
        for entry in queryset.filter(is_verified=True, user__isnull=True):
            if User.objects.filter(phone_number=entry.phone_number).exists():
                continue
            sid = entry.student_id or f"EXH{User.objects.count()+1:05d}"
            raw_password = _generate_password()
            user = User(
                username=sid,
                student_id=sid,
                first_name=entry.first_name,
                last_name=entry.last_name,
                phone_number=entry.phone_number,
                program=entry.program,
                year_of_study=entry.year_of_study,
                hall=entry.hall or '',
            )
            user.set_password(raw_password)
            user.can_vote = True
            user.changed_password = False
            user.save()
            entry.user = user
            entry.save(update_fields=['user'])
            if user.phone_number:
                try:
                    send_welcome_sms(user, raw_password, async_send=True)
                except Exception:
                    pass
            promoted_count += 1
        self.message_user(request, f"Promoted {promoted_count} verified entries to users and sent credentials.")
    promote_verified_entries.short_description = "Promote verified entries to Users (send SMS)"

    def bulk_verify_and_promote_with_sms(self, request, queryset):
        """
        Bulk verify and promote exhibition entries to users with SMS notifications.
        This is the fallback functionality for frontend issues.
        """
        from django.db import transaction
        
        verified_count = 0
        promoted_count = 0
        sms_sent_count = 0
        errors = []
        
        # Filter to only unverified entries to avoid duplicates
        unverified_entries = queryset.filter(is_verified=False)
        
        if not unverified_entries.exists():
            self.message_user(request, "No unverified entries selected.", level='warning')
            return
        
        with transaction.atomic():
            for entry in unverified_entries:
                try:
                    # Mark as verified
                    entry.is_verified = True
                    entry.verified_by = request.user
                    entry.verified_at = timezone.now()
                    verified_count += 1
                    
                    # Check if user already exists with this phone
                    if User.objects.filter(phone_number=entry.phone_number).exists():
                        entry.save()
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
                    
                    # Send SMS
                    if user.phone_number:
                        try:
                            send_welcome_sms(user, raw_password, async_send=True)
                            sms_sent_count += 1
                        except Exception as e:
                            errors.append(f"SMS failed for {user.phone_number}: {str(e)}")
                
                except Exception as e:
                    errors.append(f"Failed to process entry {entry.id}: {str(e)}")
                    continue
        
        # Provide detailed feedback
        success_msg = f"Bulk verification completed. {verified_count} entries verified, {promoted_count} users created, {sms_sent_count} SMS sent."
        if errors:
            error_msg = f" Errors: {len(errors)} (check logs for details)"
            self.message_user(request, success_msg + error_msg, level='warning')
            # Log errors for debugging
            import logging
            logger = logging.getLogger(__name__)
            for error in errors[:5]:  # Log first 5 errors
                logger.error(f"Bulk verification error: {error}")
        else:
            self.message_user(request, success_msg, level='success')
    
    bulk_verify_and_promote_with_sms.short_description = "🚀 BULK: Verify + Create Users + Send SMS (Frontend Fallback)"
