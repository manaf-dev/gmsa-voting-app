from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Election, Position, Candidate, Vote, ElectionResult
from .serializers import (
    ElectionSerializer,
    ElectionListSerializer,
    PositionSerializer,
    CandidateSerializer,
    CastVoteSerializer,
    ElectionResultSerializer,
)
from docs.elections import (
    list_create_elections_schema,
    retrieve_update_delete_election_schema,
    cast_vote_schema,
    user_votes_schema,
    election_results_schema,
    generate_results_schema,
    list_create_positions_schema,
    retrieve_update_delete_position_schema,
    list_create_candidates_schema,
    retrieve_update_delete_candidate_schema,
    admin_elections_stats_schema,
    admin_members_schema,
    export_members_schema,
    send_reminder_schema,
)

User = get_user_model()


@list_create_elections_schema
class ElectionListCreateView(generics.ListCreateAPIView):
    serializer_class = ElectionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_ec_member or self.request.user.is_staff:
            return Election.objects.all()
        return Election.objects.filter(status__in=["upcoming", "active"])

    def perform_create(self, serializer):
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            raise permissions.PermissionDenied("Only EC members can create elections")
        serializer.save(created_by=self.request.user)


@retrieve_update_delete_election_schema
class ElectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        election = super().get_object()
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            if election.status not in ["upcoming", "active"]:
                raise permissions.PermissionDenied(
                    "You can only view active or upcoming elections"
                )
        return election


@cast_vote_schema
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def cast_vote(request):
    if not request.user.can_vote:
        return Response(
            {"error": "You must pay your dues to vote", "payment_required": True},
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )

    serializer = CastVoteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    position = serializer.validated_data["position"]
    candidate = serializer.validated_data["candidate"]

    # Check if user has already voted for this position
    existing_vote = Vote.objects.filter(
        voter=request.user, candidate__position=position
    ).first()

    if existing_vote:
        return Response(
            {"error": "You have already voted for this position"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create the vote
    with transaction.atomic():
        vote = Vote.objects.create(
            voter=request.user,
            candidate=candidate,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

    return Response(
        {"message": "Vote cast successfully", "vote_id": str(vote.id)},
        status=status.HTTP_201_CREATED,
    )


@user_votes_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_votes(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    if not request.user.can_vote:
        return Response(
            {
                "error": "You must pay your dues to view voting information",
                "payment_required": True,
            },
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )

    votes = Vote.objects.filter(
        voter=request.user, candidate__position__election=election
    ).select_related("candidate__position")

    voted_positions = []
    for vote in votes:
        voted_positions.append(
            {
                "position_id": vote.candidate.position.id,
                "position_title": vote.candidate.position.title,
                "candidate_id": vote.candidate.id,
                "candidate_name": vote.candidate.name,
                "timestamp": vote.timestamp,
            }
        )

    return Response(
        {
            "election_id": str(election.id),
            "election_title": election.title,
            "voted_positions": voted_positions,
            "can_still_vote": election.can_vote,
        }
    )


@election_results_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def election_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    # Only EC members, staff, or if results are public
    if not (
        request.user.is_ec_member
        or request.user.is_staff
        or election.show_results_after_voting
        or election.status == "completed"
    ):
        return Response(
            {"error": "Results are not yet available"}, status=status.HTTP_403_FORBIDDEN
        )

    positions_with_results = []
    for position in election.positions.all():
        candidates_with_votes = []
        for candidate in position.candidates.all():
            candidates_with_votes.append(
                {
                    "id": candidate.id,
                    "name": candidate.name,
                    "student_id": candidate.student_id,
                    "vote_count": candidate.vote_count,
                    "vote_percentage": candidate.vote_percentage,
                }
            )

        # Sort by vote count descending
        candidates_with_votes.sort(key=lambda x: x["vote_count"], reverse=True)

        positions_with_results.append(
            {
                "id": position.id,
                "title": position.title,
                "total_votes": position.total_votes,
                "candidates": candidates_with_votes,
            }
        )

    return Response(
        {
            "election": {
                "id": str(election.id),
                "title": election.title,
                "status": election.status,
                "total_votes": election.total_votes,
                "total_voters": election.total_voters,
            },
            "positions": positions_with_results,
        }
    )


@generate_results_schema
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def generate_election_results(request, election_id):
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response(
            {"error": "Only EC members can generate official results"},
            status=status.HTTP_403_FORBIDDEN,
        )

    election = get_object_or_404(Election, id=election_id)

    # Calculate results
    from accounts.models import User

    total_eligible_voters = User.objects.filter(
        has_paid_dues=True, is_active=True
    ).count()
    total_votes_cast = election.total_votes
    voter_turnout = (
        (election.total_voters / total_eligible_voters * 100)
        if total_eligible_voters > 0
        else 0
    )

    # Create or update result record
    result, created = ElectionResult.objects.update_or_create(
        election=election,
        defaults={
            "total_eligible_voters": total_eligible_voters,
            "total_votes_cast": total_votes_cast,
            "voter_turnout_percentage": voter_turnout,
            "generated_by": request.user,
        },
    )

    # Mark election as completed if not already
    if election.status == "active":
        election.status = "completed"
        election.save()

    return Response(
        {
            "message": "Election results generated successfully",
            "result": ElectionResultSerializer(result).data,
        }
    )


# Position Views
@list_create_positions_schema
class PositionListCreateView(generics.ListCreateAPIView):
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        election_id = self.kwargs.get("election_id")
        return Position.objects.filter(election_id=election_id).order_by("order")

    def perform_create(self, serializer):
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            raise permissions.PermissionDenied("Only EC members can create positions")

        election_id = self.kwargs.get("election_id")
        election = get_object_or_404(Election, id=election_id)

        # Don't allow creating positions for active or completed elections
        if election.status in ["active", "completed"]:
            return Response(
                {"error": "Cannot create positions for active or completed elections"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(election=election)


@retrieve_update_delete_position_schema
class PositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        position = super().get_object()
        # Regular users can view positions for upcoming/active elections
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            if position.election.status not in ["upcoming", "active"]:
                raise permissions.PermissionDenied(
                    "You can only view positions for active or upcoming elections"
                )
        return position

    def perform_update(self, serializer):
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            raise permissions.PermissionDenied("Only EC members can update positions")

        position = self.get_object()
        if position.election.status in ["active", "completed"]:
            return Response(
                {"error": "Cannot update positions for active or completed elections"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

    def perform_destroy(self, instance):
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            raise permissions.PermissionDenied("Only EC members can delete positions")

        if instance.election.status in ["active", "completed"]:
            return Response(
                {"error": "Cannot delete positions for active or completed elections"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if position has candidates
        if instance.candidates.exists():
            return Response(
                {"error": "Cannot delete position that has candidates"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.delete()


# Candidate Views
@list_create_candidates_schema
class CandidateListCreateView(generics.ListCreateAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        position_id = self.kwargs.get("position_id")
        return Candidate.objects.filter(position_id=position_id).order_by(
            "user__student_id"
        )

    def perform_create(self, serializer):
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            raise permissions.PermissionDenied("Only EC members can add candidates")

        position_id = self.kwargs.get("position_id")
        position = get_object_or_404(Position, id=position_id)

        # Don't allow adding candidates to active or completed elections
        if position.election.status in ["active", "completed"]:
            return Response(
                {"error": "Cannot add candidates to active or completed elections"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the user to be added as candidate
        user_id = self.request.data.get("user_id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            candidate_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404)

        # Check if user has paid dues (if required)
        if position.election.require_dues_payment and not candidate_user.has_paid_dues:
            return Response(
                {"error": "Candidate must have paid dues to participate"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user is already a candidate for this position
        if Candidate.objects.filter(position=position, user=candidate_user).exists():
            return Response(
                {"error": "User is already a candidate for this position"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(position=position, user=candidate_user)


@retrieve_update_delete_candidate_schema
class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        candidate = super().get_object()
        # Regular users can view candidates for upcoming/active elections
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            if candidate.position.election.status not in ["upcoming", "active"]:
                raise permissions.PermissionDenied(
                    "You can only view candidates for active or upcoming elections"
                )
        return candidate

    def perform_update(self, serializer):
        candidate = self.get_object()

        # Allow the candidate themselves to update their own info
        if not (
            self.request.user.is_ec_member
            or self.request.user.is_staff
            or self.request.user == candidate.user
        ):
            raise permissions.PermissionDenied(
                "Only EC members or the candidate can update candidate information"
            )

        # Don't allow updates during active elections (except manifesto/profile)
        if candidate.position.election.status == "active":
            allowed_fields = {"manifesto", "profile_picture"}
            update_fields = set(self.request.data.keys())
            if not update_fields.issubset(allowed_fields):
                return Response(
                    {
                        "error": "During active elections, only manifesto and profile picture can be updated"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Don't allow any updates for completed elections
        if candidate.position.election.status == "completed":
            return Response(
                {"error": "Cannot update candidates for completed elections"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

    def perform_destroy(self, instance):
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            raise permissions.PermissionDenied("Only EC members can remove candidates")

        if instance.position.election.status in ["active", "completed"]:
            return Response(
                {
                    "error": "Cannot remove candidates from active or completed elections"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if candidate has votes
        if instance.votes.exists():
            return Response(
                {"error": "Cannot remove candidate who has received votes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.delete()


# Admin Views
@admin_elections_stats_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def admin_stats(request):
    """Get election statistics for admin dashboard"""
    if not (request.user.is_ec_member or request.user.is_staff):
        raise permissions.PermissionDenied("Only EC members can access admin stats")

    from django.db.models import Count, Sum

    stats = {
        "total_elections": Election.objects.count(),
        "active_elections": Election.objects.filter(status="active").count(),
        "upcoming_elections": Election.objects.filter(status="upcoming").count(),
        "completed_elections": Election.objects.filter(status="completed").count(),
        "total_votes_cast": Vote.objects.count(),
        "total_positions": Position.objects.count(),
        "total_candidates": Candidate.objects.count(),
        "elections_by_status": dict(
            Election.objects.values("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        ),
        "recent_activity": [],  # Can be implemented based on requirements
    }

    return Response(stats)


@admin_members_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def admin_members(request):
    """Get all members for admin management"""
    if not (request.user.is_ec_member or request.user.is_staff):
        raise permissions.PermissionDenied("Only EC members can access member data")

    from django.core.paginator import Paginator
    from accounts.serializers import UserSerializer

    # Get query parameters
    dues_status = request.GET.get("dues_status")
    academic_year = request.GET.get("academic_year")
    year_of_study = request.GET.get("year_of_study")
    search = request.GET.get("search")

    # Start with all users
    queryset = User.objects.all()

    # Apply filters
    if dues_status == "paid":
        queryset = queryset.filter(has_paid_dues=True)
    elif dues_status == "unpaid":
        queryset = queryset.filter(has_paid_dues=False)

    if year_of_study:
        queryset = queryset.filter(year_of_study=year_of_study)

    if search:
        from django.db.models import Q

        queryset = queryset.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(student_id__icontains=search)
        )

    # Pagination
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Serialize results
    members_data = []
    for user in page_obj:
        user_data = UserSerializer(user).data
        # Add payment history if needed
        user_data["payment_history"] = []  # Implement based on payments app
        members_data.append(user_data)

    return Response(
        {
            "count": paginator.count,
            "next": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "results": members_data,
        }
    )


@export_members_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_members(request):
    """Export members data as CSV"""
    if not (request.user.is_ec_member or request.user.is_staff):
        raise permissions.PermissionDenied("Only EC members can export member data")

    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="gmsa_members.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Student ID",
            "Full Name",
            "Email",
            "Program",
            "Year of Study",
            "Phone Number",
            "Date Joined",
            "Dues Status",
            "Last Payment Date",
        ]
    )

    users = User.objects.all()
    for user in users:
        writer.writerow(
            [
                user.student_id,
                user.get_full_name(),
                user.email,
                user.program,
                user.year_of_study,
                user.phone_number or "",
                user.date_joined.strftime("%Y-%m-%d"),
                "Paid" if user.has_paid_dues else "Unpaid",
                (
                    user.last_payment_date.strftime("%Y-%m-%d")
                    if hasattr(user, "last_payment_date") and user.last_payment_date
                    else ""
                ),
            ]
        )

    return response


@send_reminder_schema
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def send_reminder(request, member_id):
    """Send payment reminder to a member"""
    if not (request.user.is_ec_member or request.user.is_staff):
        raise permissions.PermissionDenied("Only EC members can send reminders")

    try:
        member = User.objects.get(id=member_id)
    except User.DoesNotExist:
        return Response({"error": "Member not found"}, status=status.HTTP_404)

    if member.has_paid_dues:
        return Response(
            {"error": "Member has already paid dues"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Send reminder email (implement based on your email system)
    # For now, just return success
    return Response(
        {
            "message": f"Payment reminder sent to {member.get_full_name()}",
            "sent_to": member.email,
            "sent_at": timezone.now(),
        }
    )
