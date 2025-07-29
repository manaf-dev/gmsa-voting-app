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
    summary="Cast vote in an election",
    description="""
    Cast a vote for a candidate in a specific position within an election.
    
    Requirements:
    - User must have paid dues for the current academic year
    - Election must be active
    - User cannot vote twice for the same position
    - Candidate must belong to the specified position
    
    Returns success message and vote confirmation.
    """,
    request=CastVoteSerializer,
    responses={
        201: inline_serializer(
            name="VoteSuccessSerializer",
            fields={
                "message": serializers.CharField(),
                "vote_id": serializers.UUIDField(),
                "candidate_name": serializers.CharField(),
                "position_title": serializers.CharField(),
            },
        ),
        400: inline_serializer(
            name="VoteErrorSerializer",
            fields={
                "error": serializers.CharField(),
                "details": serializers.CharField(required=False),
            },
        ),
        402: inline_serializer(
            name="CastVotePaymentRequiredSerializer",
            fields={
                "error": serializers.CharField(),
                "payment_url": serializers.URLField(required=False),
            },
        ),
    },
    tags=["Voting"],
)

user_votes_schema = extend_schema(
    summary="Get current user's votes for an election",
    description="""
    Retrieve all votes cast by the current user in a specific election.
    Returns the positions they've voted for and when they voted.
    
    Note: Actual candidate votes remain anonymous - this only shows which positions
    the user has participated in.
    """,
    request=None,
    responses={
        200: inline_serializer(
            name="UserVotesSerializer",
            fields={
                "election_id": serializers.UUIDField(),
                "election_title": serializers.CharField(),
                "voted_positions": inline_serializer(
                    name="VotedPositionSerializer",
                    fields={
                        "position_id": serializers.IntegerField(),
                        "position_title": serializers.CharField(),
                        "candidate_id": serializers.IntegerField(),
                        "candidate_name": serializers.CharField(),
                        "timestamp": serializers.DateTimeField(),
                    },
                    many=True,
                ),
                "total_positions": serializers.IntegerField(),
                "positions_voted": serializers.IntegerField(),
            },
        ),
        402: inline_serializer(
            name="UserVotesPaymentRequiredSerializer",
            fields={
                "error": serializers.CharField(),
                "payment_url": serializers.URLField(required=False),
            },
        ),
    },
    tags=["Voting"],
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
    tags=["Elections"],
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
    tags=["Elections", "Positions"],
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
    tags=["Elections", "Positions"],
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
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="The ID of the position",
        ),
    ],
    responses={
        200: CandidateSerializer(many=True),
        201: CandidateSerializer,
    },
    tags=["Elections", "Candidates"],
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
    tags=["Elections", "Candidates"],
)

# Admin schemas
admin_elections_stats_schema = extend_schema(
    summary="Get election statistics for admin dashboard",
    description="""
    Retrieve comprehensive statistics about elections for the admin dashboard.
    Only EC members and staff can access this endpoint.
    
    Returns counts of elections by status, voting statistics, and other metrics.
    """,
    request=None,
    responses={
        200: inline_serializer(
            name="AdminElectionStatsSerializer",
            fields={
                "total_elections": serializers.IntegerField(),
                "active_elections": serializers.IntegerField(),
                "upcoming_elections": serializers.IntegerField(),
                "completed_elections": serializers.IntegerField(),
                "total_votes_cast": serializers.IntegerField(),
                "total_positions": serializers.IntegerField(),
                "total_candidates": serializers.IntegerField(),
                "elections_by_status": serializers.DictField(),
                "recent_activity": serializers.ListField(),
            },
        ),
    },
    tags=["Admin", "Statistics"],
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
    tags=["Admin", "Members"],
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
    tags=["Admin", "Export"],
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
    tags=["Admin", "Members"],
)
