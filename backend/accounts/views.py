import csv
from io import StringIO
import secrets
import select
import string
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, AcademicYear
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    AcademicYearSerializer,
)
from .selectors import get_all_users, get_user_by_id
from docs.accounts import (
    register_user_schema,
    bulk_registration_schema,
    login_schema,
    retrieve_user_schema,
    reset_user_password_schema,
    send_voting_reminders_schema,
)


@reset_user_password_schema
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reset_user_password(request):
    """
    Reset a user's password (Admin/EC only)

    Expected payload:
    {
        "student_id": "12345678"
    }
    """
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response(
            {"error": "Only EC members can reset passwords"},
            status=status.HTTP_403_FORBIDDEN,
        )

    student_id = request.data.get("student_id")
    if not student_id:
        return Response(
            {"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(student_id=student_id)
    except User.DoesNotExist:
        return Response(
            {"error": f"User with student ID {student_id} not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not user.phone_number:
        return Response(
            {"error": "User has no phone number for SMS notification"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Generate new password
    import secrets
    import string

    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    new_password = "".join(secrets.choice(characters) for _ in range(10))

    # Set new password
    user.set_password(new_password)
    user.save()

    # Send SMS notification
    try:
        from utils.sms_service import send_password_reset_sms

        sms_result = send_password_reset_sms(user, new_password, async_send=True)

        if sms_result["success"]:
            return Response(
                {
                    "message": f"Password reset successful for {user.student_id}",
                    # "sms_queued": True,
                    # "task_id": sms_result.get("task_id"),
                    "new_password": new_password,  # Return for admin reference
                    "phone_number": user.phone_number,
                }
            )
        else:
            return Response(
                {
                    "message": f"Password reset successful for {user.student_id}",
                    # "sms_queued": False,
                    # "sms_error": sms_result.get("error"),
                    "new_password": new_password,  # Return for admin reference
                    "phone_number": user.phone_number,
                }
            )
    except Exception as e:
        return Response(
            {
                "message": f"Password reset successful for {user.student_id}",
                # "sms_queued": False,
                # "sms_error": str(e),
                "new_password": new_password,  # Return for admin reference
                "phone_number": user.phone_number,
            }
        )


@send_voting_reminders_schema
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def send_voting_reminders(request):
    """
    Send voting reminders to users who haven't voted in active elections
    """
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response(
            {"error": "Only EC members can send voting reminders"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        from elections.models import Election, Vote
        from utils.tasks import send_voting_reminder_task

        # Get active elections
        active_elections = Election.objects.filter(status="active")

        if not active_elections:
            return Response(
                {"message": "No active elections found", "reminders_sent": 0}
            )

        total_queued = 0
        task_ids = []

        for election in active_elections:
            # Get users who haven't voted in this election
            voted_user_ids = (
                Vote.objects.filter(candidate__position__election=election)
                .values_list("voter_id", flat=True)
                .distinct()
            )

            eligible_users = (
                User.objects.filter(
                    can_vote=True, is_active=True, phone_number__isnull=False
                )
                .exclude(phone_number__exact="")
                .exclude(id__in=voted_user_ids)
            )

            for user in eligible_users:
                task = send_voting_reminder_task.delay(user.id, election.id)
                task_ids.append(task.id)
                total_queued += 1

        if total_queued == 0:
            return Response(
                {
                    "message": "No users found who need voting reminders",
                    "reminders_queued": 0,
                }
            )

        return Response(
            {
                "message": "Voting reminders sent to voters",
                "reminders_sent": total_queued,
                # "task_ids": task_ids[:10],  # Return first 10 task IDs
                # "total_tasks": len(task_ids),
            }
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to send voting reminders: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class UserViewset(viewsets.ViewSet):
    """Viewset for user operations"""

    def _generate_random_password(self, length=10):
        """Generate a random password with letters, digits, and punctuation."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(characters) for _ in range(length))

    @register_user_schema
    def register_user(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"detail": "Registration successful"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @bulk_registration_schema
    def bulk_registration(self, request):

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_file = file.read().decode("utf-8")
            csv_data = StringIO(decoded_file)
            reader = csv.DictReader(csv_data)

            # check if required fields are present
            required_fields = [
                "username",
                "email",
                "first_name",
                "last_name",
                "student_id",
                "phone_number",
                "year_of_study",
            ]
            for field in required_fields:
                if field not in reader.fieldnames:
                    return Response(
                        {f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            for row in reader:
                # generate password
                row["password"] = row["confirm_password"] = (
                    self._generate_random_password()
                )
                serializer = UserRegistrationSerializer(data=row)
                if serializer.is_valid():
                    user = serializer.save()
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {"detail": "Users registered successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @login_schema
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

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

    def logout(self, request):
        if request.user.is_authenticated:
            try:
                request.user.auth_token.delete()
            except:
                pass
            logout(request)
        return Response({"message": "Logout successful"})

    def list_users(self, request):
        """List all users"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        users = get_all_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve_user(self, request, user_id):
        """Retrieve a user by ID"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = get_user_by_id(user_id)
        if not user:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(user)
        return Response(serializer.data)

class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Issue access/refresh tokens and set the refresh token in an HttpOnly cookie.

    Response body will only include the access token and user info can be fetched separately.
    """

    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Pull tokens
        access = data.get("access")
        refresh = data.get("refresh")

        # Build response with only access token
        response = Response({"access": access}, status=status.HTTP_200_OK)

        # Set refresh cookie
        if refresh:
            cookie_name = getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh_token")
            cookie_secure = getattr(settings, "JWT_COOKIE_SECURE", False)
            cookie_samesite = getattr(settings, "JWT_COOKIE_SAMESITE", "Lax")
            # Compute cookie max_age from SIMPLE_JWT setting
            refresh_lifetime = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")
            max_age = int(refresh_lifetime.total_seconds()) if refresh_lifetime else None
            response.set_cookie(
                cookie_name,
                refresh,
                max_age=max_age,
                httponly=True,
                secure=cookie_secure,
                samesite=cookie_samesite,
                path="/",
            )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh access (and rotated refresh) using the refresh token stored in an HttpOnly cookie.

    If a rotated refresh is returned, update the cookie. Response body includes only the access token.
    """

    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        cookie_name = getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh_token")
        provided_refresh = request.data.get("refresh") if hasattr(request, "data") else None
        cookie_refresh = request.COOKIES.get(cookie_name)

        data = {"refresh": provided_refresh or cookie_refresh}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        access = validated.get("access")
        new_refresh = validated.get("refresh")

        response = Response({"access": access}, status=status.HTTP_200_OK)

        # If rotation is enabled and a new refresh is issued, update cookie
        if new_refresh:
            cookie_secure = getattr(settings, "JWT_COOKIE_SECURE", False)
            cookie_samesite = getattr(settings, "JWT_COOKIE_SAMESITE", "Lax")
            refresh_lifetime = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")
            max_age = int(refresh_lifetime.total_seconds()) if refresh_lifetime else None
            response.set_cookie(
                cookie_name,
                new_refresh,
                max_age=max_age,
                httponly=True,
                secure=cookie_secure,
                samesite=cookie_samesite,
                path="/",
            )

        return response


class JWTLogoutView(APIView):
    """
    Blacklist the refresh token (from cookie or request body) and clear the cookie.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        cookie_name = getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh_token")
        token = request.data.get("refresh") if hasattr(request, "data") else None
        token = token or request.COOKIES.get(cookie_name)

        response = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)

        # Clear cookie regardless of blacklist success
        response.delete_cookie(cookie_name, path="/")

        if token:
            try:
                refresh = RefreshToken(token)
                # Blacklist if app is enabled
                try:
                    refresh.blacklist()
                except Exception:
                    # Blacklist not configured or token already blacklisted
                    pass
            except Exception:
                # Invalid token; still return 200 after clearing cookie
                pass

        return response

    @retrieve_user_schema
    def retrieve_user(self, request, user_id):
        """Retrieve a single user by ID"""
        user = get_user_by_id(user_id)
        if not user:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserSerializer(user)
        return Response(serializer.data)


# class MemberListView(generics.ListAPIView):
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         if not self.request.user.is_ec_member and not self.request.user.is_staff:
#             return User.objects.none()
#         return User.objects.all().order_by("-date_joined")


# @api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
# def academic_years_view(request):
#     """Get all academic years"""
#     years = AcademicYear.objects.all()
#     return Response(
#         {
#             "academic_years": AcademicYearSerializer(years, many=True).data,
#             "current_year": AcademicYear.get_current_year_string(),
#         }
#     )


# @api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
# def payment_status_view(request):
#     """Check user's payment status for current and previous years"""
#     user = request.user
#     current_year = user.current_academic_year

#     # Get payment status for current year
#     current_payment = user.get_dues_payment_for_year(current_year)

#     # Get all payment history
#     all_payments = user.get_all_dues_payments()

#     return Response(
#         {
#             "current_academic_year": current_year,
#             "has_paid_current_dues": user.has_paid_current_dues,
#             "can_vote": user.can_vote,
#             "current_payment": {
#                 "paid": bool(current_payment),
#                 "payment_date": (
#                     current_payment.payment.transaction_date
#                     if current_payment
#                     else None
#                 ),
#                 "amount": current_payment.payment.amount if current_payment else None,
#             },
#             "payment_history": [
#                 {
#                     "academic_year": dp.academic_year,
#                     "amount": dp.payment.amount,
#                     "payment_date": dp.payment.transaction_date,
#                     "is_current_year": dp.is_current_year,
#                 }
#                 for dp in all_payments
#             ],
#             "user_info": {
#                 "year_of_study": user.year_of_study,
#                 "is_current_student": user.is_current_student,
#                 "years_since_admission": user.years_since_admission,
#             },
#         }
#     )
