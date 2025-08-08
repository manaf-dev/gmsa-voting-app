from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from accounts.serializers import (
    ChangePasswordSerializer,
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

change_password_schema = extend_schema(
    summary="Change user password",
    description="This endpoint allows a user to change their password.",
    request=ChangePasswordSerializer,
    responses={
        200: inline_serializer(
            name="ChangePasswordSuccessSerializer",
            fields={
                "message": serializers.CharField(),
            },
        ),
    },
    tags=["Users"],
)

add_user_schema = extend_schema(
    summary="Add a new user (Admin/EC only)",
    description="This endpoint allows EC members and staff to add a new user.",
    request=inline_serializer(
        name="AddUserRequestSerializer",
        fields={
            "username": serializers.CharField(required=True),
            "email": serializers.EmailField(required=True),
            "first_name": serializers.CharField(required=True),
            "last_name": serializers.CharField(required=True),
            "student_id": serializers.CharField(required=True),
            "phone_number": serializers.CharField(required=True),
            "year_of_study": serializers.CharField(required=True),
            "program": serializers.CharField(required=True),
            "admission_year": serializers.CharField(required=True),
        },
    ),
    responses={201: UserSerializer},
    tags=["Admin"],
)

reset_user_password_schema = extend_schema(
    summary="Reset user password (Admin/EC only)",
    description="""
    This endpoint allows EC members and staff to reset a user's password and send SMS notification.
    """,
    request=inline_serializer(
        name="ResetPasswordRequestSerializer",
        fields={
            "student_id": serializers.CharField(
                required=True,
                help_text="Student ID of the user whose password should be reset",
            ),
        },
    ),
    responses={
        200: inline_serializer(
            name="ResetPasswordSuccessSerializer",
            fields={
                "message": serializers.CharField(),
                "new_password": serializers.CharField(),
                "phone_number": serializers.CharField(),
            },
        ),
    },
    tags=["Users"],
)

send_voting_reminders_schema = extend_schema(
    summary="Send voting reminders (Admin/EC only)",
    description="""
    This endpoint sends voting reminders to users who haven't voted in active elections.    
    """,
    request=None,  # No request body needed
    responses={
        200: inline_serializer(
            name="VotingRemindersSuccessSerializer",
            fields={
                "message": serializers.CharField(),
                "reminders_queued": serializers.IntegerField(),
                # "task_ids": serializers.ListField(
                #     child=serializers.CharField(),
                #     help_text="List of Celery task IDs (first 10 shown)",
                # ),
                # "total_tasks": serializers.IntegerField(),
            },
        ),
    },
    tags=["Admin"],
)
