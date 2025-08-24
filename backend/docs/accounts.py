from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from rest_framework import serializers
from accounts.serializers import (
    ChangePasswordSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserUpdateSerializer,
)


exhibition_lookup_schema = extend_schema(
    summary="Exhibition lookup by phone",
    description="Check if a phone number already exists in either the exhibition register or active users.",
    request=inline_serializer(name="ExhibitionLookupRequest", fields={
        'phone': serializers.CharField()
    }),
    responses={200: inline_serializer(name="ExhibitionLookupResponse", fields={
        'status': serializers.CharField(),
        'message': serializers.CharField(),
    })},
    tags=["Exhibition"],
)

exhibition_register_schema = extend_schema(
    summary="Register details for exhibition",
    description="Submit basic voter details to the exhibition (staging) register pending verification.",
    request=inline_serializer(name="ExhibitionRegisterRequest", fields={
        'phone': serializers.CharField(),
        'first_name': serializers.CharField(),
        'last_name': serializers.CharField(),
        'student_id': serializers.CharField(required=False, allow_blank=True),
        'program': serializers.CharField(required=False, allow_blank=True),
        'year_of_study': serializers.CharField(required=False, allow_blank=True),
    }),
    responses={201: inline_serializer(name="ExhibitionRegisterResponse", fields={
        'status': serializers.CharField(),
        'message': serializers.CharField(),
    })},
    tags=["Exhibition"],
)

exhibition_pending_list_schema = extend_schema(
    summary="List pending exhibition entries (EC only)",
    description="Return up to 500 pending (unverified) exhibition entries.",
    responses={200: inline_serializer(name="ExhibitionPendingListResponse", fields={
        'pending': serializers.ListField(child=serializers.DictField())
    })},
    tags=["Exhibition"],
)

exhibition_verify_schema = extend_schema(
    summary="Verify exhibition entry (EC only)",
    description="Mark a single exhibition entry as verified.",
    responses={200: inline_serializer(name="ExhibitionVerifyResponse", fields={
        'status': serializers.CharField(),
        'entry_id': serializers.CharField(),
    })},
    tags=["Exhibition"],
)

exhibition_promote_schema = extend_schema(
    summary="Promote verified entries (EC only)",
    description="Promote up to 500 verified exhibition entries into real voter accounts and dispatch welcome SMS.",
    responses={200: inline_serializer(name="ExhibitionPromoteResponse", fields={
        'promoted': serializers.ListField(child=serializers.DictField()),
        'count': serializers.IntegerField(),
    })},
    tags=["Exhibition"],
)

exhibition_verify_promote_schema = extend_schema(
    summary="Verify & promote single entry (EC only)",
    description="One-click endpoint to verify and immediately promote an exhibition entry with credentials SMS.",
    responses={201: inline_serializer(name="ExhibitionVerifyPromoteResponse", fields={
        'status': serializers.CharField(),
        'entry_id': serializers.CharField(),
        'user': serializers.DictField(),
        'sms_sent': serializers.BooleanField(),
    })},
    tags=["Exhibition"],
)

exhibition_entries_list_schema = extend_schema(
    summary="List exhibition entries (EC only)",
    description="List exhibition entries with optional filters: status (pending|verified|all), search, limit.",
    parameters=[
        OpenApiParameter(name='status', description='pending | verified | all', required=False, type=str),
        OpenApiParameter(name='search', description='Search term for phone, name, student_id', required=False, type=str),
        OpenApiParameter(name='limit', description='Max records (default 200, max 1000)', required=False, type=int),
    ],
    responses={200: inline_serializer(name="ExhibitionEntriesListResponse", fields={
        'count': serializers.IntegerField(),
        'entries': serializers.ListField(child=serializers.DictField()),
    })},
    tags=["Exhibition"],
)

exhibition_bulk_verify_schema = extend_schema(
    summary="Bulk verify all exhibition entries (EC only)",
    description="""
    Verify all unverified exhibition entries at once and create user accounts for each.
    This will:
    1. Mark all unverified entries as verified
    2. Create user accounts with generated credentials
    3. Send welcome SMS to each new user
    
    Returns counts of verified entries, created users, and SMS sent.
    """,
    request=None,
    responses={200: inline_serializer(name="ExhibitionBulkVerifyResponse", fields={
        'status': serializers.CharField(),
        'message': serializers.CharField(),
        'verified_count': serializers.IntegerField(),
        'promoted_count': serializers.IntegerField(),
        'sms_sent_count': serializers.IntegerField(),
        'errors': serializers.ListField(child=serializers.CharField()),
    })},
    tags=["Exhibition"],
)

exhibition_reverify_schema = extend_schema(
    summary="Reverify exhibition entry (EC only)",
    description="""
    Reverify a verified exhibition entry that has already been promoted to a user account.
    This will:
    1. Generate a new password for the user
    2. Send a new welcome SMS with updated credentials
    
    Use this when a verified user reports not receiving their SMS credentials.
    """,
    request=None,
    responses={200: inline_serializer(name="ExhibitionReverifyResponse", fields={
        'status': serializers.CharField(),
        'message': serializers.CharField(),
        'user_id': serializers.CharField(),
        'phone': serializers.CharField(),
        'sms_sent': serializers.BooleanField(),
    })},
    tags=["Exhibition"],
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
                "access": serializers.CharField(),
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

update_user_schema = extend_schema(
    summary="Update user details",
    description="This endpoints updates details of specific user",
    request=UserUpdateSerializer,
    responses={200: UserSerializer},
    tags=["Users"]
)

remove_user_schema = extend_schema(
    summary="Remove user",
    description="This endpoints removes user from active users on the system",
    request=None,
    responses={200: inline_serializer(
            name="RemoveResponse",
            fields={
                "message": serializers.CharField(),
            },
        ),},
    tags=["Users"]
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
