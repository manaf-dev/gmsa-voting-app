from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from .models import User, UserProfile, AcademicYear
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    AcademicYearSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        UserProfile.objects.create(user=user)
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
                "message": "Registration successful",
                "payment_required": not user.has_paid_current_dues,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]

        # Check if user has paid current year dues
        if not user.can_vote:
            return Response(
                {
                    "error": f"You must pay your dues for the {user.current_academic_year} academic year before accessing the system",
                    "payment_required": True,
                    "user_id": user.id,
                    "academic_year": user.current_academic_year,
                    "user_info": {
                        "username": user.username,
                        "year_of_study": user.year_of_study,
                        "is_current_student": user.is_current_student,
                    },
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
                "message": "Login successful",
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout_view(request):
    if request.user.is_authenticated:
        try:
            request.user.auth_token.delete()
        except:
            pass
        logout(request)
    return Response({"message": "Logout successful"})


@api_view(["GET"])
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get user's dues payment history
    dues_payments = user.get_all_dues_payments()

    return Response(
        {
            "user": UserSerializer(user).data,
            "profile": UserProfileSerializer(profile).data,
            "dues_history": [
                {
                    "academic_year": dp.academic_year,
                    "amount": dp.payment.amount,
                    "payment_date": dp.payment.transaction_date,
                    "is_current_year": dp.is_current_year,
                }
                for dp in dues_payments
            ],
        }
    )


@api_view(["PUT"])
def update_profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    user_serializer = UserSerializer(
        user, data=request.data.get("user", {}), partial=True
    )
    profile_serializer = UserProfileSerializer(
        profile, data=request.data.get("profile", {}), partial=True
    )

    if user_serializer.is_valid() and profile_serializer.is_valid():
        user_serializer.save()
        profile_serializer.save()
        return Response(
            {
                "user": user_serializer.data,
                "profile": profile_serializer.data,
                "message": "Profile updated successfully",
            }
        )

    errors = {}
    if not user_serializer.is_valid():
        errors.update(user_serializer.errors)
    if not profile_serializer.is_valid():
        errors.update(profile_serializer.errors)

    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class MemberListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_ec_member and not self.request.user.is_staff:
            return User.objects.none()
        return User.objects.all().order_by("-date_joined")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def academic_years_view(request):
    """Get all academic years"""
    years = AcademicYear.objects.all()
    return Response(
        {
            "academic_years": AcademicYearSerializer(years, many=True).data,
            "current_year": AcademicYear.get_current_year_string(),
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def payment_status_view(request):
    """Check user's payment status for current and previous years"""
    user = request.user
    current_year = user.current_academic_year

    # Get payment status for current year
    current_payment = user.get_dues_payment_for_year(current_year)

    # Get all payment history
    all_payments = user.get_all_dues_payments()

    return Response(
        {
            "current_academic_year": current_year,
            "has_paid_current_dues": user.has_paid_current_dues,
            "can_vote": user.can_vote,
            "current_payment": {
                "paid": bool(current_payment),
                "payment_date": (
                    current_payment.payment.transaction_date
                    if current_payment
                    else None
                ),
                "amount": current_payment.payment.amount if current_payment else None,
            },
            "payment_history": [
                {
                    "academic_year": dp.academic_year,
                    "amount": dp.payment.amount,
                    "payment_date": dp.payment.transaction_date,
                    "is_current_year": dp.is_current_year,
                }
                for dp in all_payments
            ],
            "user_info": {
                "year_of_study": user.year_of_study,
                "is_current_student": user.is_current_student,
                "years_since_admission": user.years_since_admission,
            },
        }
    )
