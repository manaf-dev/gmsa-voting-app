from django.db import models
from django.conf import settings
import uuid


class Payment(models.Model):
    PAYMENT_TYPES = [
        ("dues", "Membership Dues"),
        ("donation", "Anonymous Donation"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="GHS")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Paystack fields
    paystack_reference = models.CharField(max_length=100, unique=True)
    paystack_access_code = models.CharField(max_length=100, blank=True)
    paystack_authorization_url = models.URLField(blank=True)

    # Transaction details
    transaction_date = models.DateTimeField(null=True, blank=True)
    gateway_response = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.get_payment_type_display()} - {self.amount} {self.currency}"

    @property
    def is_successful(self):
        return self.status == "successful"


class DuesPayment(models.Model):
    """Track dues payments for specific academic years"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dues_payments"
    )
    payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, related_name="dues_payment"
    )
    academic_year = models.CharField(max_length=20, help_text="e.g., '2024/2025'")
    semester = models.CharField(
        max_length=20,
        default="Full Year",
        choices=[
            ("Full Year", "Full Year"),
            ("First", "First Semester"),
            ("Second", "Second Semester"),
        ],
    )

    class Meta:
        unique_together = ["user", "academic_year"]
        ordering = ["-academic_year"]

    def __str__(self):
        return f"{self.user.username} - Dues {self.academic_year}"

    @property
    def is_current_year(self):
        """Check if this payment is for the current academic year"""
        from accounts.models import AcademicYear

        current_year = AcademicYear.get_current_year_string()
        return self.academic_year == current_year


class Donation(models.Model):
    """Track anonymous donations"""

    payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, related_name="donation"
    )
    donor_name = models.CharField(max_length=100, blank=True)  # Optional for anonymous
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=True)

    def __str__(self):
        name = (
            self.donor_name
            if not self.is_anonymous and self.donor_name
            else "Anonymous"
        )
        return f"Donation from {name} - {self.payment.amount} {self.payment.currency}"


class PaymentCallback(models.Model):
    """Store webhook callbacks from Paystack"""

    reference = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50)
    data = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.reference}"


class PaymentReminder(models.Model):
    """Track payment reminders sent to users"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_reminders",
    )
    academic_year = models.CharField(max_length=20)
    reminder_type = models.CharField(
        max_length=20,
        choices=[("email", "Email"), ("sms", "SMS"), ("system", "System Notification")],
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "academic_year", "reminder_type"]

    def __str__(self):
        return f"Reminder to {self.user.username} for {self.academic_year}"
