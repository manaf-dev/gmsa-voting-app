from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from payments.serializers import (
    DuesPaymentSerializer,
    DonationSerializer,
    PaymentSerializer,
)


# Payment schemas
initiate_dues_payment_schema = extend_schema(
    summary="Initiate dues payment",
    description="""
    Initiate a membership dues payment for the current academic year.
    
    This endpoint:
    1. Creates a payment record
    2. Generates a Paystack payment URL
    3. Returns the payment URL for the frontend to redirect the user
    
    The amount is automatically set based on the current dues amount configured in settings.
    Users can only pay once per academic year.
    """,
    request=inline_serializer(
        name="InitiateDuesPaymentSerializer",
        fields={
            "academic_year": serializers.CharField(
                help_text="Academic year in format 2024/2025. Optional - defaults to current year."
            ),
        },
    ),
    responses={
        201: inline_serializer(
            name="PaymentInitiatedSerializer",
            fields={
                "payment_id": serializers.UUIDField(),
                "payment_url": serializers.URLField(),
                "amount": serializers.DecimalField(max_digits=10, decimal_places=2),
                "academic_year": serializers.CharField(),
                "reference": serializers.CharField(),
            },
        ),
        400: inline_serializer(
            name="PaymentErrorSerializer",
            fields={
                "error": serializers.CharField(),
                "details": serializers.CharField(required=False),
            },
        ),
    },
    tags=["Payments"],
)

initiate_donation_schema = extend_schema(
    summary="Initiate donation payment",
    description="""
    Initiate a donation payment to GMSA.
    
    This endpoint:
    1. Creates a donation record
    2. Generates a Paystack payment URL
    3. Returns the payment URL for the frontend to redirect the user
    
    Users can specify any amount and optionally remain anonymous.
    """,
    request=DonationSerializer,
    responses={
        201: inline_serializer(
            name="DonationInitiatedSerializer",
            fields={
                "payment_id": serializers.UUIDField(),
                "payment_url": serializers.URLField(),
                "amount": serializers.DecimalField(max_digits=10, decimal_places=2),
                "is_anonymous": serializers.BooleanField(),
                "reference": serializers.CharField(),
            },
        ),
        400: inline_serializer(
            name="DonationErrorSerializer",
            fields={
                "error": serializers.CharField(),
                "details": serializers.CharField(required=False),
            },
        ),
    },
    tags=["Payments"],
)

verify_payment_schema = extend_schema(
    summary="Verify payment with Paystack",
    description="""
    Verify a payment transaction with Paystack and update the local payment record.
    
    This endpoint is typically called:
    1. By the frontend after user returns from Paystack
    2. By Paystack webhook (if configured)
    
    On successful verification:
    - Updates payment status to 'completed'
    - Updates user's dues payment status (for dues payments)
    - Sends confirmation email to user
    """,
    parameters=[
        OpenApiParameter(
            name="reference",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="The Paystack payment reference",
        ),
    ],
    responses={
        200: inline_serializer(
            name="PaymentVerifiedSerializer",
            fields={
                "status": serializers.CharField(),
                "message": serializers.CharField(),
                "payment": PaymentSerializer(),
                "verified_at": serializers.DateTimeField(),
            },
        ),
        400: inline_serializer(
            name="VerificationErrorSerializer",
            fields={
                "error": serializers.CharField(),
                "details": serializers.CharField(required=False),
            },
        ),
        404: inline_serializer(
            name="PaymentNotFoundSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Payments"],
)

user_payments_schema = extend_schema(
    summary="Get current user's payment history",
    description="""
    Retrieve the payment history for the current authenticated user.
    
    Returns:
    - All dues payments by academic year
    - All donations made
    - Payment status and dates
    - Total amounts paid
    
    Payments are ordered by date (most recent first).
    """,
    parameters=[
        OpenApiParameter(
            name="payment_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by payment type",
            enum=["dues", "donation"],
        ),
        OpenApiParameter(
            name="academic_year",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by academic year (for dues payments)",
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by payment status",
            enum=["pending", "completed", "failed", "cancelled"],
        ),
    ],
    responses={
        200: inline_serializer(
            name="UserPaymentsSerializer",
            fields={
                "count": serializers.IntegerField(),
                "results": PaymentSerializer(many=True),
                "summary": inline_serializer(
                    name="PaymentSummarySerializer",
                    fields={
                        "total_dues_paid": serializers.DecimalField(
                            max_digits=10, decimal_places=2
                        ),
                        "total_donations": serializers.DecimalField(
                            max_digits=10, decimal_places=2
                        ),
                        "current_year_dues_status": serializers.CharField(),
                        "dues_by_year": serializers.DictField(),
                    },
                ),
            },
        ),
    },
    tags=["Payments"],
)

payment_callback_schema = extend_schema(
    summary="Paystack payment callback/webhook",
    description="""
    Webhook endpoint for Paystack payment notifications.
    
    This endpoint is called by Paystack when payment status changes.
    It verifies the webhook signature and updates the payment status accordingly.
    
    This endpoint should be configured in your Paystack dashboard as the webhook URL.
    """,
    request=inline_serializer(
        name="PaystackWebhookSerializer",
        fields={
            "event": serializers.CharField(),
            "data": serializers.DictField(),
        },
    ),
    responses={
        200: inline_serializer(
            name="WebhookProcessedSerializer",
            fields={
                "status": serializers.CharField(),
                "message": serializers.CharField(),
            },
        ),
        400: inline_serializer(
            name="WebhookErrorSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Payments", "Webhooks"],
)

# Admin payment schemas
admin_payments_schema = extend_schema(
    summary="Get all payments for admin management",
    description="""
    Retrieve a list of all payments made by all users.
    Only EC members and staff can access this endpoint.
    
    Includes filtering options for payment type, status, date range, etc.
    Useful for financial reporting and payment tracking.
    """,
    parameters=[
        OpenApiParameter(
            name="payment_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by payment type",
            enum=["dues", "donation"],
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by payment status",
            enum=["pending", "completed", "failed", "cancelled"],
        ),
        OpenApiParameter(
            name="academic_year",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by academic year",
        ),
        OpenApiParameter(
            name="date_from",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Filter payments from this date",
        ),
        OpenApiParameter(
            name="date_to",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Filter payments to this date",
        ),
    ],
    responses={
        200: inline_serializer(
            name="AdminPaymentsSerializer",
            fields={
                "count": serializers.IntegerField(),
                "next": serializers.URLField(allow_null=True),
                "previous": serializers.URLField(allow_null=True),
                "results": PaymentSerializer(many=True),
                "summary": inline_serializer(
                    name="AdminPaymentSummarySerializer",
                    fields={
                        "total_dues_collected": serializers.DecimalField(
                            max_digits=10, decimal_places=2
                        ),
                        "total_donations_collected": serializers.DecimalField(
                            max_digits=10, decimal_places=2
                        ),
                        "pending_payments": serializers.IntegerField(),
                        "completed_payments": serializers.IntegerField(),
                        "failed_payments": serializers.IntegerField(),
                        "members_paid_current_year": serializers.IntegerField(),
                        "members_unpaid_current_year": serializers.IntegerField(),
                    },
                ),
            },
        ),
    },
    tags=["Admin", "Payments"],
)

export_payments_schema = extend_schema(
    summary="Export payment data as CSV",
    description="""
    Export payment data as a CSV file for financial reporting.
    Only EC members and staff can access this endpoint.
    
    Applies the same filters as the admin payments list endpoint.
    Returns a CSV file with payment details, user information, and transaction data.
    """,
    parameters=[
        OpenApiParameter(
            name="payment_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by payment type",
            enum=["dues", "donation"],
        ),
        OpenApiParameter(
            name="academic_year",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by academic year",
        ),
        OpenApiParameter(
            name="date_from",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Filter payments from this date",
        ),
        OpenApiParameter(
            name="date_to",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Filter payments to this date",
        ),
    ],
    responses={
        200: inline_serializer(
            name="PaymentCSVExportSerializer",
            fields={
                "file": serializers.FileField(),
            },
        ),
    },
    tags=["Admin", "Export"],
)

payment_stats_schema = extend_schema(
    summary="Get payment statistics for admin dashboard",
    description="""
    Retrieve comprehensive payment statistics for the admin dashboard.
    Only EC members and staff can access this endpoint.
    
    Returns financial metrics, payment trends, and dues payment status.
    """,
    responses={
        200: inline_serializer(
            name="PaymentStatsSerializer",
            fields={
                "total_revenue": serializers.DecimalField(
                    max_digits=10, decimal_places=2
                ),
                "dues_revenue": serializers.DecimalField(
                    max_digits=10, decimal_places=2
                ),
                "donations_revenue": serializers.DecimalField(
                    max_digits=10, decimal_places=2
                ),
                "current_year_dues": inline_serializer(
                    name="CurrentYearDuesSerializer",
                    fields={
                        "total_expected": serializers.DecimalField(
                            max_digits=10, decimal_places=2
                        ),
                        "total_collected": serializers.DecimalField(
                            max_digits=10, decimal_places=2
                        ),
                        "collection_rate": serializers.FloatField(),
                        "members_paid": serializers.IntegerField(),
                        "members_unpaid": serializers.IntegerField(),
                    },
                ),
                "monthly_trends": serializers.ListField(
                    child=inline_serializer(
                        name="MonthlyTrendSerializer",
                        fields={
                            "month": serializers.CharField(),
                            "dues": serializers.DecimalField(
                                max_digits=10, decimal_places=2
                            ),
                            "donations": serializers.DecimalField(
                                max_digits=10, decimal_places=2
                            ),
                            "total": serializers.DecimalField(
                                max_digits=10, decimal_places=2
                            ),
                        },
                    )
                ),
                "recent_payments": PaymentSerializer(many=True),
            },
        ),
    },
    tags=["Admin", "Statistics"],
)
