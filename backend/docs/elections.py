from urllib import request
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from elections.serializers import (
    ElectionSerializer,
    ElectionListSerializer,
    PositionSerializer,
    CandidateSerializer,
    CastVoteSerializer,
    BulkCastVoteSerializer,
    ElectionResultSerializer,
)


# Election schemas
list_create_elections_schema = extend_schema(
    summary="List elections or create a new election",
    description="""
    GET: List all elections. Regular users see only upcoming and active elections.
    EC members and staff see all elections.
    
    POST: Create a new election. Only EC members and staff can create elections.
    The election will include positions that can be added separately via the positions endpoint.
    """,
    request=ElectionListSerializer,
    responses={
        200: ElectionListSerializer(many=True),
        201: ElectionListSerializer,
    },
    tags=["Elections"],
)

retrieve_update_delete_election_schema = extend_schema(
    summary="Retrieve, update, or delete an election",
    description="""
    GET: Retrieve detailed information about a specific election including positions and candidates.
    Regular users can only view upcoming and active elections.
    
    PUT/PATCH: Update election details. Only EC members and staff can update elections.
    
    DELETE: Delete an election. Only EC members and staff can delete elections.
    """,
    request=ElectionSerializer,
    responses={
        200: ElectionSerializer,
        204: None,
    },
    tags=["Elections"],
)

cast_vote_schema = extend_schema(
    summary="Cast votes (single or full ballot) with anonymous encryption",
    description="""
    Submit your ballot for an election.

    Two modes are supported:
    1) Bulk ballot (recommended):
       {
         "election_id": "<uuid>",
         "selections": [
           { "position_id": "<uuid>", "candidate_id": "<uuid>" },
           ...
         ]
       }

    2) Single-position vote (legacy):
       { "position_id": "<uuid>", "candidate_id": "<uuid>" }

    Requirements:
    - Election must be active
    - Candidate must belong to the specified position
    - Exactly one selection per position (one vote per position)
    - Voter cannot vote twice for the same position (checked anonymously)

    Security Features:
    - Anonymous storage: no direct FK links to voter/candidate
    - Encrypted vote payloads
    - Digital signatures and integrity hashing
    - Audit logging and session tracking
    """,
    request=BulkCastVoteSerializer,
    responses={
        201: inline_serializer(
            name="CastVoteSuccess",
            fields={
                "message": serializers.CharField(),
                # Bulk mode returns count; single mode returns verification/timestamp.
                "count": serializers.IntegerField(required=False),
                "verified": serializers.BooleanField(required=False),
                "timestamp": serializers.DateTimeField(required=False),
            },
        ),
        400: inline_serializer(
            name="CastVoteError",
            fields={
                "error": serializers.CharField(),
                "details": serializers.CharField(required=False),
            },
        ),
    },
    tags=["Voting", "Security"],
)

user_votes_schema = extend_schema(
    summary="Get current user's voting status for an election",
    description="""
    Retrieve the voting status for the current user in a specific election.
    Due to the anonymous voting system, this endpoint shows which positions
    the user has voted for without revealing their actual candidate choices.
    
    Returns:
    - Which positions the user has participated in
    - Timestamps of when votes were cast
    - Total positions available vs positions voted
    
    Note: Individual candidate choices remain completely anonymous and encrypted.
    Even administrators cannot trace specific votes back to voters without
    decryption keys and explicit authorization.
    """,
    request=None,
    responses={
        200: inline_serializer(
            name="UserVotesSerializer",
            fields={
                "election_id": serializers.UUIDField(),
                "election_title": serializers.CharField(),
                "user_has_voted": serializers.BooleanField(),
                "positions_voted": inline_serializer(
                    name="VotedPositionSerializer",
                    fields={
                        "position_id": serializers.IntegerField(),
                        "position_title": serializers.CharField(),
                        "has_voted": serializers.BooleanField(),
                        "vote_timestamp": serializers.DateTimeField(allow_null=True),
                    },
                    many=True,
                ),
                "total_positions": serializers.IntegerField(),
                "positions_voted_count": serializers.IntegerField(),
            },
        ),
        402: inline_serializer(
            name="UserVotesPaymentRequiredSerializer",
            fields={
                "error": serializers.CharField(),
                "payment_required": serializers.BooleanField(),
            },
        ),
    },
    tags=["Voting", "Security"],
)

election_results_schema = extend_schema(
    summary="Get election results",
    description="""
    Retrieve the results of a completed election or live results of an active election.
    
    For completed elections: Shows final vote counts and percentages.
    For active elections: May show live results if enabled in election settings.
    For upcoming elections: Returns error.
    
    Results include:
    - Vote counts per candidate
    - Vote percentages
    - Total votes cast
    - Voter turnout statistics
    """,
    request=None,
    responses={
        200: inline_serializer(
            name="ElectionResultsSerializer",
            fields={
                "election": ElectionSerializer(),
                "results": inline_serializer(
                    name="PositionResultSerializer",
                    fields={
                        "position": PositionSerializer(),
                        "candidates": inline_serializer(
                            name="CandidateResultSerializer",
                            fields={
                                "candidate": CandidateSerializer(),
                                "vote_count": serializers.IntegerField(),
                                "vote_percentage": serializers.FloatField(),
                            },
                            many=True,
                        ),
                        "total_votes": serializers.IntegerField(),
                    },
                    many=True,
                ),
                "stats": inline_serializer(
                    name="ElectionResultsStatsSerializer",
                    fields={
                        "total_eligible_voters": serializers.IntegerField(),
                        "total_voters": serializers.IntegerField(),
                        "voter_turnout_percentage": serializers.FloatField(),
                        "total_votes_cast": serializers.IntegerField(),
                    },
                ),
            },
        ),
        400: inline_serializer(
            name="ResultsErrorSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Admin"],
)

generate_results_schema = extend_schema(
    summary="Generate and finalize election results",
    description="""
    Generate final results for a completed election. This endpoint is typically called
    automatically when an election ends, but can be manually triggered by EC members.
    
    Only EC members and staff can access this endpoint.
    
    This will:
    - Calculate final vote counts and percentages
    - Create ElectionResult records
    - Mark the election as completed if not already
    """,
    request=None,
    responses={
        200: inline_serializer(
            name="GenerateResultsSerializer",
            fields={
                "message": serializers.CharField(),
                "election_id": serializers.UUIDField(),
                "results_generated_at": serializers.DateTimeField(),
            },
        ),
        400: inline_serializer(
            name="GenerateResultsErrorSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Elections", "Admin"],
)

# Position schemas
list_create_positions_schema = extend_schema(
    summary="List positions or create a new position",
    description="""
    GET: List all positions for a specific election.
    
    POST: Create a new position within an election. Only EC members and staff can create positions.
    Positions define the roles that candidates can run for in an election.
    """,
    parameters=[
        OpenApiParameter(
            name="election_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="The UUID of the election",
        ),
    ],
    request=PositionSerializer,
    responses={
        200: PositionSerializer(many=True),
        201: PositionSerializer,
    },
    tags=["Positions"],
)

retrieve_update_delete_position_schema = extend_schema(
    summary="Retrieve, update, or delete a position",
    description="""
    GET: Retrieve detailed information about a specific position including candidates.
    
    PUT/PATCH: Update position details. Only EC members and staff can update positions.
    
    DELETE: Delete a position. Only EC members and staff can delete positions.
    Note: Cannot delete positions that have candidates or votes.
    """,
    request=PositionSerializer,
    responses={
        200: PositionSerializer,
        204: None,
    },
    tags=["Positions"],
)

# Candidate schemas
list_create_candidates_schema = extend_schema(
    summary="List candidates or create a new candidate",
    description="""
    GET: List all candidates for a specific position.
    
    POST: Add a new candidate to a position. Only EC members and staff can add candidates.
    Candidates must be registered users who have paid their dues.
    """,
    request=CandidateSerializer,
    parameters=[
        OpenApiParameter(
            name="position_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="The ID of the position",
        ),
    ],
    responses={
        200: CandidateSerializer(many=True),
        201: CandidateSerializer,
    },
    tags=["Candidates"],
)

retrieve_update_delete_candidate_schema = extend_schema(
    summary="Retrieve, update, or delete a candidate",
    description="""
    GET: Retrieve detailed information about a specific candidate.
    
    PUT/PATCH: Update candidate details (manifesto, profile picture, etc.).
    Only EC members, staff, or the candidate themselves can update.
    
    DELETE: Remove a candidate from a position. Only EC members and staff can remove candidates.
    Note: Cannot remove candidates if voting has started.
    """,
    request=CandidateSerializer,
    responses={
        200: CandidateSerializer,
        204: None,
    },
    tags=["Candidates"],
)

# Admin schemas
admin_elections_stats_schema = extend_schema(
    summary="Get election statistics for admin dashboard",
    description="""
    Retrieve comprehensive statistics about elections for the admin dashboard.
    Only EC members and staff can access this endpoint.
    
    Currently returns only the requested high-level stats: total elections, total members, and eligible voters.
    """,
    request=None,
    responses={
        200: inline_serializer(
            name="AdminElectionStatsSerializer",
            fields={
                "total_elections": serializers.IntegerField(),
                "total_members": serializers.IntegerField(),
                "eligible_voters": serializers.IntegerField(),
            },
        ),
    },
    tags=["Admin"],
)

admin_members_schema = extend_schema(
    summary="Get all members for admin management",
    description="""
    Retrieve a list of all registered members with their dues payment status
    and voting eligibility. Only EC members and staff can access this endpoint.
    
    Supports filtering by dues status, academic year, and year of study.
    Includes pagination for large member lists.
    """,
    request=None,
    parameters=[
        OpenApiParameter(
            name="academic_year",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by academic year (e.g., 2024/2025)",
        ),
        OpenApiParameter(
            name="year_of_study",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by year of study (1-6)",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by name, email, or student ID",
        ),
    ],
    responses={
        200: inline_serializer(
            name="AdminMembersSerializer",
            fields={
                "count": serializers.IntegerField(),
                "next": serializers.URLField(allow_null=True),
                "previous": serializers.URLField(allow_null=True),
                "results": inline_serializer(
                    name="MemberWithStatusSerializer",
                    fields={
                        "id": serializers.IntegerField(),
                        "full_name": serializers.CharField(),
                        "email": serializers.EmailField(),
                        "student_id": serializers.CharField(),
                        "program": serializers.CharField(),
                        "year_of_study": serializers.CharField(),
                        "phone_number": serializers.CharField(allow_null=True),
                        "date_joined": serializers.DateTimeField(),
                    },
                    many=True,
                ),
            },
        ),
    },
    tags=["Admin"],
)

export_members_excel_schema = extend_schema(
    summary="Export exhibition register as Excel",
    description="""
    Export exhibition register data as an Excel file. Only EC members and staff can access this endpoint.
    
    Returns an Excel (.xlsx) file with exhibition entry information including:
    - Personal details (name, student ID, phone number)
    - Academic information (year of study, program, hall)
    - Registration details (source, verification status, date registered)
    - Verification information (verified by, verified at)
    - User account creation status
    
    The exported file includes color coding:
    - Green rows for verified entries
    - Yellow rows for pending entries
    """,
    request=None,
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search in name, student ID, phone number, program, hall, or year of study",
        ),
    ],
    responses={
        200: {
            "description": "Excel file download",
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
    },
    tags=["Admin"],
)

export_members_schema = extend_schema(
    summary="Export members data as CSV",
    description="""
    Export member data as a CSV file. Only EC members and staff can access this endpoint.
    
    Applies the same filters as the members list endpoint.
    Returns a CSV file with member information and payment status.
    """,
    request=None,
    parameters=[
        OpenApiParameter(
            name="academic_year",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by academic year (e.g., 2024/2025)",
        ),
    ],
    responses={
        200: inline_serializer(
            name="CSVExportSerializer",
            fields={
                "file": serializers.FileField(),
            },
        ),
    },
    tags=["Admin"],
)

send_reminder_schema = extend_schema(
    summary="Send payment reminder to a member",
    description="""
    Send a payment reminder email to a specific member who hasn't paid their dues.
    Only EC members and staff can send reminders.
    """,
    request=None,
    parameters=[
        OpenApiParameter(
            name="member_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="The ID of the member to send reminder to",
        ),
    ],
    responses={
        200: inline_serializer(
            name="ReminderSentSerializer",
            fields={
                "message": serializers.CharField(),
                "sent_to": serializers.EmailField(),
                "sent_at": serializers.DateTimeField(),
            },
        ),
        400: inline_serializer(
            name="ReminderErrorSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Admin"],
)

# Security schemas
security_status_schema = extend_schema(
    summary="Get security status for an election",
    description="""
    Retrieve comprehensive security status and configuration for a specific election.
    Only EC members and staff can access this endpoint.
    
    Returns:
    - Security configuration (encryption, signatures, audit logging)
    - System security checks (keys configured, rate limiting active)
    - Voting statistics (total votes, secure votes, verification rates)
    - Audit trail summary
    - Overall security status
    """,
    request=None,
    parameters=[
        OpenApiParameter(
            name="election_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="The UUID of the election",
        ),
    ],
    responses={
        200: inline_serializer(
            name="SecurityStatusSerializer",
            fields={
                "election_id": serializers.UUIDField(),
                "election_title": serializers.CharField(),
                "security_configuration": inline_serializer(
                    name="SecurityConfigSerializer",
                    fields={
                        "vote_encryption_enabled": serializers.BooleanField(),
                        "digital_signatures_enabled": serializers.BooleanField(),
                        "audit_logging_enabled": serializers.BooleanField(),
                        "ip_verification_enabled": serializers.BooleanField(),
                        "two_factor_required": serializers.BooleanField(),
                    },
                ),
                "system_security": inline_serializer(
                    name="SystemSecuritySerializer",
                    fields={
                        "encryption_keys_configured": serializers.BooleanField(),
                        "signing_keys_configured": serializers.BooleanField(),
                        "audit_logging_active": serializers.BooleanField(),
                        "rate_limiting_active": serializers.BooleanField(),
                    },
                ),
                "voting_statistics": inline_serializer(
                    name="VotingStatsSerializer",
                    fields={
                        "total_votes": serializers.IntegerField(),
                        "secure_votes": serializers.IntegerField(),
                        "verified_votes": serializers.IntegerField(),
                        "encryption_rate": serializers.FloatField(),
                        "verification_rate": serializers.FloatField(),
                    },
                ),
                "audit_trail": inline_serializer(
                    name="AuditSummarySerializer",
                    fields={
                        "total_audit_entries": serializers.IntegerField(),
                    },
                ),
                "status": serializers.CharField(),
            },
        ),
        403: inline_serializer(
            name="SecurityStatusForbiddenSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Security", "Admin"],
)

verify_vote_integrity_schema = extend_schema(
    summary="Verify the cryptographic integrity of a vote",
    description="""
    Verify the cryptographic integrity of a specific vote using digital signatures
    and hash verification. Only EC members and staff can verify votes.
    
    This process:
    - Verifies the digital signature authenticity
    - Checks the cryptographic hash integrity
    - Updates the vote's verification status
    - Creates an audit log entry for the verification
    
    Used for forensic analysis and ensuring vote authenticity.
    """,
    request=None,
    parameters=[
        OpenApiParameter(
            name="vote_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="The UUID of the vote to verify",
        ),
    ],
    responses={
        200: inline_serializer(
            name="VoteIntegritySerializer",
            fields={
                "vote_id": serializers.UUIDField(),
                "is_valid": serializers.BooleanField(),
                "integrity_verified": serializers.BooleanField(),
                "signature_verified": serializers.BooleanField(),
                "timestamp": serializers.DateTimeField(),
                "verification_performed_by": serializers.CharField(),
                "verification_timestamp": serializers.DateTimeField(),
            },
        ),
        403: inline_serializer(
            name="VerifyVoteForbiddenSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
        404: inline_serializer(
            name="VoteNotFoundSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Security", "Admin"],
)

audit_trail_schema = extend_schema(
    summary="Get audit trail for an election",
    description="""
    Retrieve the comprehensive audit trail for a specific election.
    Only EC members and staff can access audit trails.
    
    Returns the latest 100 audit log entries including:
    - All voting activities
    - Election management actions
    - Security events
    - Admin access logs
    - System events
    
    Each entry includes cryptographic integrity hashes for tamper detection.
    """,
    request=None,
    parameters=[
        OpenApiParameter(
            name="election_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="The UUID of the election",
        ),
    ],
    responses={
        200: inline_serializer(
            name="AuditTrailSerializer",
            fields={
                "election_id": serializers.UUIDField(),
                "election_title": serializers.CharField(),
                "audit_trail": inline_serializer(
                    name="AuditLogEntrySerializer",
                    fields={
                        "id": serializers.UUIDField(),
                        "timestamp": serializers.DateTimeField(),
                        "action": serializers.CharField(),
                        "user": serializers.CharField(),
                        "resource_type": serializers.CharField(),
                        "resource_id": serializers.CharField(),
                        "ip_address": serializers.IPAddressField(),
                        "details": serializers.DictField(),
                        "integrity_hash": serializers.CharField(),
                    },
                    many=True,
                ),
                "total_entries": serializers.IntegerField(),
                "generated_at": serializers.DateTimeField(),
                "generated_by": serializers.CharField(),
            },
        ),
        403: inline_serializer(
            name="AuditTrailForbiddenSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Security", "Admin"],
)

suspicious_activity_schema = extend_schema(
    summary="Get suspicious activity report",
    description="""
    Retrieve a report of all suspicious voting activities detected by the system.
    Only EC members and staff can access this endpoint.
    
    Suspicious activities include:
    - Unusually high number of votes in a session
    - IP address changes during voting
    - User agent changes during voting
    - Rapid voting patterns
    - Multiple simultaneous sessions
    
    Used for security monitoring and fraud detection.
    """,
    request=None,
    responses={
        200: inline_serializer(
            name="SuspiciousActivitySerializer",
            fields={
                "suspicious_activities": inline_serializer(
                    name="SuspiciousSessionSerializer",
                    fields={
                        "session_id": serializers.UUIDField(),
                        "user": serializers.CharField(),
                        "election": serializers.CharField(),
                        "session_start": serializers.DateTimeField(),
                        "session_end": serializers.DateTimeField(allow_null=True),
                        "ip_address": serializers.IPAddressField(),
                        "votes_cast": serializers.IntegerField(),
                        "suspicious_reason": serializers.CharField(),
                        "country_code": serializers.CharField(allow_null=True),
                        "city": serializers.CharField(allow_null=True),
                    },
                    many=True,
                ),
                "total_suspicious_sessions": serializers.IntegerField(),
                "generated_at": serializers.DateTimeField(),
                "generated_by": serializers.CharField(),
            },
        ),
        403: inline_serializer(
            name="SuspiciousActivityForbiddenSerializer",
            fields={
                "error": serializers.CharField(),
            },
        ),
    },
    tags=["Security", "Admin"],
)
