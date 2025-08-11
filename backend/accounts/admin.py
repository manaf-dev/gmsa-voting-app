from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, AcademicYear


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
            "GMSA Information",
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
