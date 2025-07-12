from django.contrib import admin
from .models import Payment, DuesPayment, Donation, PaymentCallback


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "payment_type",
        "amount",
        "status",
        "paystack_reference",
        "created_at",
    )
    list_filter = ("payment_type", "status", "created_at")
    search_fields = ("user__username", "paystack_reference", "user__email")
    readonly_fields = (
        "paystack_reference",
        "paystack_access_code",
        "paystack_authorization_url",
        "transaction_date",
        "gateway_response",
        "created_at",
        "updated_at",
    )


@admin.register(DuesPayment)
class DuesPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "academic_year",
        "semester",
        "payment_status",
        "payment_date",
    )
    list_filter = ("academic_year", "semester", "payment__status")
    search_fields = ("user__username", "user__email", "user__student_id")

    def payment_status(self, obj):
        return obj.payment.status

    payment_status.short_description = "Payment Status"

    def payment_date(self, obj):
        return obj.payment.transaction_date

    payment_date.short_description = "Payment Date"


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("donor_display", "amount", "is_anonymous", "payment_date")
    list_filter = ("is_anonymous", "payment__status")
    search_fields = ("donor_name", "message")

    def donor_display(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        return obj.donor_name or "Anonymous"

    donor_display.short_description = "Donor"

    def amount(self, obj):
        return f"{obj.payment.amount} {obj.payment.currency}"

    amount.short_description = "Amount"

    def payment_date(self, obj):
        return obj.payment.transaction_date

    payment_date.short_description = "Date"


@admin.register(PaymentCallback)
class PaymentCallbackAdmin(admin.ModelAdmin):
    list_display = ("reference", "event_type", "processed", "created_at")
    list_filter = ("event_type", "processed", "created_at")
    search_fields = ("reference",)
    readonly_fields = ("reference", "event_type", "data", "created_at")
