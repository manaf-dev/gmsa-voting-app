from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import datetime


class YEAR_CHOICES(models.TextChoices):
    LEVEL_100 = "100", "Level 100"
    LEVEL_200 = "200", "Level 200"
    LEVEL_300 = "300", "Level 300"
    LEVEL_400 = "400", "Level 400"
    GRADUATE = "graduate", "Graduate"
    ALUMNI = "alumni", "Alumni"


class User(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    student_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    year_of_study = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True)
    program = models.CharField(max_length=100, blank=True)
    admission_year = models.IntegerField(
        null=True, blank=True, help_text="Year student was admitted"
    )
    is_ec_member = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    can_vote = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student_id} - {self.get_full_name() or self.username}"

    def save(self, *args, **kwargs):
        """Override save to set admission year if not provided"""
        if not self.admission_year:
            if self.year_of_study in ["100", "200", "300", "400"]:
                self.admission_year = datetime.now().year - int(self.year_of_study[0])
            else:
                self.admission_year = datetime.now().year

        super().save(*args, **kwargs)

    @property
    def current_academic_year(self):
        """Get current academic year (e.g., '2024/2025')"""
        now = datetime.now()
        if now.month >= 9:  # Academic year starts in September
            return f"{now.year}/{now.year + 1}"
        else:
            return f"{now.year - 1}/{now.year}"

    @property
    def display_name(self):
        return (
            f"{self.first_name} {self.last_name}" if self.first_name else self.username
        )

    @property
    def is_current_student(self):
        """Check if user is still a current student (not graduated)"""
        return self.year_of_study in ["100", "200", "300", "400"]

    @property
    def years_since_admission(self):
        """Calculate years since admission"""
        if not self.admission_year:
            return 0
        current_year = datetime.now().year
        return current_year - self.admission_year

    def should_graduate(self):
        """Check if student should be marked as graduate based on years since admission"""
        return self.years_since_admission >= 4 and self.is_current_student

    # @property
    # def has_paid_current_dues(self):
    #     """Check if user has paid dues for current academic year"""
    #     current_year = self.current_academic_year
    #     return self.dues_payments.filter(
    #         academic_year=current_year, payment__status="successful"
    #     ).exists()

    # @property
    # def can_vote(self):
    #     """Check if user can vote based on current year dues payment and active status"""
    #     return (
    #         self.has_paid_current_dues
    #         and self.is_active
    #         and self.year_of_study not in ["graduate", "alumni"]
    #     )

    # def get_dues_payment_for_year(self, academic_year=None):
    #     """Get dues payment for specific academic year"""
    #     if not academic_year:
    #         academic_year = self.current_academic_year

    #     return self.dues_payments.filter(
    #         academic_year=academic_year, payment__status="successful"
    #     ).first()

    # def get_all_dues_payments(self):
    #     """Get all successful dues payments"""
    #     return self.dues_payments.filter(payment__status="successful").order_by(
    #         "-academic_year"
    #     )


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
#     bio = models.TextField(blank=True)
#     social_media_handles = models.JSONField(default=dict, blank=True)

#     def __str__(self):
#         return f"{self.user.username}'s Profile"


class AcademicYear(models.Model):
    """Track academic years and dues amounts"""

    year = models.CharField(max_length=20, unique=True, help_text="e.g., '2024/2025'")
    dues_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    is_current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year"]

    def __str__(self):
        return f"Academic Year {self.year}"

    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one academic year is marked as current
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_current_year(cls):
        """Get the current academic year object"""
        return cls.objects.filter(is_current=True).first()

    @classmethod
    def get_current_year_string(cls):
        """Get current academic year as string"""
        current = cls.get_current_year()
        if current:
            return current.year

        # Fallback to calculated year if no current year is set
        now = datetime.now()
        if now.month >= 9:
            return f"{now.year}/{now.year + 1}"
        else:
            return f"{now.year - 1}/{now.year}"
