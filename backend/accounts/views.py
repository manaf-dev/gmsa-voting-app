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
from .models import User, AcademicYear
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    AcademicYearSerializer,
)
from .selectors import get_all_users, get_user_by_id
from docs.accounts import *


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
