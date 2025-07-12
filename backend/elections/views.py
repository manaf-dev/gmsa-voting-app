from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Q
from .models import Election, Position, Candidate, Vote, ElectionResult
from .serializers import (
    ElectionSerializer,
    ElectionListSerializer,
    PositionSerializer,
    CandidateSerializer,
    CastVoteSerializer,
    ElectionResultSerializer,
)


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
