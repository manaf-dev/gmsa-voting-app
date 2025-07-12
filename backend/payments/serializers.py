from rest_framework import serializers
from .models import Payment, DuesPayment, Donation
from accounts.models import AcademicYear


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            "user",
            "paystack_reference",
            "paystack_access_code",
            "paystack_authorization_url",
            "transaction_date",
            "gateway_response",
        )


class InitiatePaymentSerializer(serializers.Serializer):
    payment_type = serializers.ChoiceField(choices=Payment.PAYMENT_TYPES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    academic_year = serializers.CharField(max_length=20, required=False)
    donor_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)
    is_anonymous = serializers.BooleanField(default=True, required=False)

    def validate(self, attrs):
        payment_type = attrs.get("payment_type")

        if payment_type == "dues":
            # For dues, get amount from academic year or use default
            academic_year = attrs.get("academic_year")
            if academic_year:
                year_obj = AcademicYear.objects.filter(year=academic_year).first()
                if year_obj:
                    attrs["amount"] = year_obj.dues_amount
                else:
                    # Use default if academic year not found
                    from django.conf import settings

                    attrs["amount"] = settings.GMSA_DUES_AMOUNT
            else:
                # Use current year's amount
                current_year = AcademicYear.get_current_year()
                if current_year:
                    attrs["amount"] = current_year.dues_amount
                    attrs["academic_year"] = current_year.year
                else:
                    from django.conf import settings

                    attrs["amount"] = settings.GMSA_DUES_AMOUNT
                    # Set current academic year string
                    attrs["academic_year"] = AcademicYear.get_current_year_string()

        elif payment_type == "donation":
            # For donations, amount is required
            if not attrs.get("amount"):
                raise serializers.ValidationError("Amount is required for donations")
            if attrs["amount"] <= 0:
                raise serializers.ValidationError("Amount must be greater than 0")

        return attrs


class DuesPaymentSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    is_current_year = serializers.ReadOnlyField()

    class Meta:
        model = DuesPayment
        fields = "__all__"


class DonationSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = "__all__"
