import requests
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Payment, DuesPayment, Donation, PaymentCallback
from .serializers import (
    PaymentSerializer,
    InitiatePaymentSerializer,
    DuesPaymentSerializer,
    DonationSerializer,
)
from accounts.models import AcademicYear


class InitiatePaymentView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow anonymous donations

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment_type = serializer.validated_data["payment_type"]
        amount = serializer.validated_data.get("amount")
        academic_year = serializer.validated_data.get("academic_year")

        # For dues payments, user must be authenticated
        if payment_type == "dues" and not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required for dues payment"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Handle dues payment logic
        if payment_type == "dues":
            user = request.user

            # Use current academic year if not specified
            if not academic_year:
                academic_year = user.current_academic_year

            # Check if user has already paid for this academic year
            existing_payment = user.get_dues_payment_for_year(academic_year)
            if existing_payment:
                return Response(
                    {
                        "error": f"You have already paid your dues for {academic_year}",
                        "existing_payment": {
                            "academic_year": academic_year,
                            "amount": existing_payment.payment.amount,
                            "payment_date": existing_payment.payment.transaction_date,
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get dues amount for the academic year
            academic_year_obj = AcademicYear.objects.filter(year=academic_year).first()
            if academic_year_obj:
                amount = academic_year_obj.dues_amount
            else:
                # Fallback to default amount
                amount = Decimal(settings.GMSA_DUES_AMOUNT)

        # Generate unique reference
        import uuid

        reference = f"gmsa_{payment_type}_{uuid.uuid4().hex[:12]}"

        # Create payment record
        payment_metadata = serializer.validated_data.copy()
        payment_metadata["academic_year"] = academic_year

        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            payment_type=payment_type,
            amount=amount,
            paystack_reference=reference,
            metadata=payment_metadata,
        )

        # Initialize Paystack transaction
        paystack_data = {
            "reference": reference,
            "amount": int(amount * 100),  # Paystack expects amount in kobo
            "email": (
                request.user.email
                if request.user.is_authenticated
                else "anonymous@gmsa.com"
            ),
            "currency": "GHS",
            "callback_url": f"{request.build_absolute_uri('/api/payments/callback/')}",
            "metadata": {
                "payment_id": str(payment.id),
                "payment_type": payment_type,
                "user_id": (
                    str(request.user.id) if request.user.is_authenticated else None
                ),
                "academic_year": academic_year,
            },
        }

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                headers=headers,
                data=json.dumps(paystack_data),
            )
            response.raise_for_status()
            result = response.json()

            if result["status"]:
                payment.paystack_access_code = result["data"]["access_code"]
                payment.paystack_authorization_url = result["data"]["authorization_url"]
                payment.save()

                return Response(
                    {
                        "payment_id": str(payment.id),
                        "reference": reference,
                        "authorization_url": result["data"]["authorization_url"],
                        "access_code": result["data"]["access_code"],
                        "amount": amount,
                        "currency": "GHS",
                        "academic_year": academic_year,
                        "payment_type": payment_type,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                payment.status = "failed"
                payment.gateway_response = result.get("message", "Unknown error")
                payment.save()
                return Response(
                    {
                        "error": "Failed to initialize payment",
                        "details": result.get("message"),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except requests.exceptions.RequestException as e:
            payment.status = "failed"
            payment.gateway_response = str(e)
            payment.save()
            return Response(
                {"error": "Payment service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Verify webhook signature
        signature = request.headers.get("x-paystack-signature")
        body = request.body

        import hmac
        import hashlib

        expected_signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(), body, hashlib.sha512
        ).hexdigest()

        if signature != expected_signature:
            return Response(
                {"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        event = data.get("event")

        # Store webhook data
        PaymentCallback.objects.create(
            reference=data.get("data", {}).get("reference", ""),
            event_type=event,
            data=data,
        )

        if event == "charge.success":
            self.handle_successful_payment(data["data"])

        return Response({"status": "success"})

    def handle_successful_payment(self, data):
        reference = data.get("reference")

        try:
            payment = Payment.objects.get(paystack_reference=reference)

            with transaction.atomic():
                payment.status = "successful"
                payment.transaction_date = timezone.now()
                payment.gateway_response = json.dumps(data)
                payment.save()

                # Handle specific payment types
                if payment.payment_type == "dues" and payment.user:
                    academic_year = payment.metadata.get(
                        "academic_year", payment.user.current_academic_year
                    )

                    # Create dues payment record
                    DuesPayment.objects.create(
                        user=payment.user, payment=payment, academic_year=academic_year
                    )

                elif payment.payment_type == "donation":
                    # Create donation record
                    metadata = payment.metadata or {}
                    Donation.objects.create(
                        payment=payment,
                        donor_name=metadata.get("donor_name", ""),
                        message=metadata.get("message", ""),
                        is_anonymous=metadata.get("is_anonymous", True),
                    )

        except Payment.DoesNotExist:
            pass  # Log this error in production


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def verify_payment(request, reference):
    """Verify payment status directly with Paystack"""
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}", headers=headers
        )
        response.raise_for_status()
        result = response.json()

        if result["status"] and result["data"]["status"] == "success":
            # Update local payment record
            try:
                payment = Payment.objects.get(paystack_reference=reference)
                if payment.status == "pending":
                    # Process the payment
                    PaystackWebhookView().handle_successful_payment(result["data"])

                return Response(
                    {"status": "success", "payment": PaymentSerializer(payment).data}
                )
            except Payment.DoesNotExist:
                return Response(
                    {"error": "Payment record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {
                    "status": "failed",
                    "message": result.get("data", {}).get(
                        "gateway_response", "Payment failed"
                    ),
                }
            )

    except requests.exceptions.RequestException:
        return Response(
            {"error": "Unable to verify payment"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_payments(request):
    """Get user's payment history"""
    payments = Payment.objects.filter(user=request.user)
    dues_payments = DuesPayment.objects.filter(user=request.user)

    return Response(
        {
            "payments": PaymentSerializer(payments, many=True).data,
            "dues_payments": DuesPaymentSerializer(dues_payments, many=True).data,
            "current_academic_year": request.user.current_academic_year,
            "has_paid_current_dues": request.user.has_paid_current_dues,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def payment_stats(request):
    """Get payment statistics (for EC members)"""
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response(
            {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
        )

    from django.db.models import Sum, Count
    from accounts.models import User

    current_year = AcademicYear.get_current_year_string()

    # Current year dues statistics
    total_current_students = User.objects.filter(
        is_active=True, year_of_study__in=["100", "200", "300", "400"]
    ).count()
    paid_current_year = DuesPayment.objects.filter(
        academic_year=current_year, payment__status="successful"
    ).count()

    current_year_dues = Payment.objects.filter(
        payment_type="dues",
        status="successful",
        dues_payment__academic_year=current_year,
    )
    total_current_dues_amount = (
        current_year_dues.aggregate(Sum("amount"))["amount__sum"] or 0
    )

    # All-time dues statistics
    all_dues_payments = Payment.objects.filter(payment_type="dues", status="successful")
    total_dues_amount = all_dues_payments.aggregate(Sum("amount"))["amount__sum"] or 0

    # Donation statistics
    donations = Payment.objects.filter(payment_type="donation", status="successful")
    total_donations = donations.aggregate(Sum("amount"))["amount__sum"] or 0
    donation_count = donations.count()

    # Academic year breakdown
    academic_year_stats = []
    for year_obj in AcademicYear.objects.all()[:5]:  # Last 5 years
        year_payments = DuesPayment.objects.filter(
            academic_year=year_obj.year, payment__status="successful"
        ).count()
        year_amount = (
            Payment.objects.filter(
                payment_type="dues",
                status="successful",
                dues_payment__academic_year=year_obj.year,
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        academic_year_stats.append(
            {
                "year": year_obj.year,
                "payments_count": year_payments,
                "total_amount": year_amount,
                "is_current": year_obj.is_current,
            }
        )

    return Response(
        {
            "current_year": {
                "academic_year": current_year,
                "total_current_students": total_current_students,
                "paid_students": paid_current_year,
                "payment_rate": (
                    (paid_current_year / total_current_students * 100)
                    if total_current_students > 0
                    else 0
                ),
                "total_amount": total_current_dues_amount,
            },
            "all_time_dues": {
                "total_amount": total_dues_amount,
                "payment_count": all_dues_payments.count(),
            },
            "donations": {
                "total_amount": total_donations,
                "donation_count": donation_count,
            },
            "academic_years": academic_year_stats,
            "overall": {
                "total_revenue": float(total_dues_amount) + float(total_donations),
                "total_transactions": all_dues_payments.count() + donation_count,
            },
        }
    )
