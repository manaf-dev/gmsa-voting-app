from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from accounts.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
)


register_user_schema = extend_schema(
    summary="Register a new user",
    description="This endpoint allows a new user to register by providing their details.",
    request=UserRegistrationSerializer,
    responses={201: UserSerializer},
    tags=["Users"],
)

bulk_registration_schema = extend_schema(
    summary="Bulk register users",
    description="This endpoint allows bulk registration of users by uploading a CSV file containing user details.",
    request=inline_serializer(
        name="BulkRegistrationSerializer",
        fields={"file": serializers.FileField(required=True)},
    ),
    responses={201: UserSerializer},
    tags=["Users"],
)

login_schema = extend_schema(
    summary="User login",
    description="""
    This endpoint allows a user to log in using either their username or student ID.
    
    **Authentication Options:**
    - Username + Password
    - Student ID + Password
    
    **Example Login Methods:**
    - Username: "john_doe" with password
    - Student ID: "CS2023001" with password
    
    On successful login, returns user details and authentication token.
    """,
    request=UserLoginSerializer,
    responses={
        200: inline_serializer(
            name="LoginSuccessSerializer",
            fields={
                "user": UserSerializer(),
                "token": serializers.CharField(),
                "message": serializers.CharField(),
            },
        ),
        400: inline_serializer(
            name="LoginErrorSerializer",
            fields={
                "error": serializers.CharField(),
                "details": serializers.CharField(required=False),
            },
        ),
    },
    tags=["Users"],
)

retrieve_user_schema = extend_schema(
    summary="Retrieve user details",
    description="This endpoint retrieves the details of a specific user by their ID.",
    responses={200: UserSerializer},
    tags=["Users"],
)
