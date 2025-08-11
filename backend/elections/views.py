from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    Election,
    Position,
    Candidate,
    Vote,
    ElectionResult,
    AuditLog,
    VotingSession,
    ElectionSecurity,
)
from .serializers import (
    ElectionSerializer,
    ElectionListSerializer,
    PositionSerializer,
    CandidateSerializer,
    CastVoteSerializer,
    BulkCastVoteSerializer,
)
from .crypto import check_security_configuration
from utils.helpers import absolute_media_url_builder
from docs.elections import (
    list_create_elections_schema,
    retrieve_update_delete_election_schema,
    cast_vote_schema,
    election_results_schema,
    list_create_positions_schema,
    retrieve_update_delete_position_schema,
    list_create_candidates_schema,
    retrieve_update_delete_candidate_schema,
    admin_elections_stats_schema,
    admin_members_schema,
    export_members_schema,
    send_reminder_schema,
    security_status_schema,
    verify_vote_integrity_schema,
    audit_trail_schema,
    suspicious_activity_schema,
)

User = get_user_model()


@list_create_elections_schema
class ElectionListCreateView(generics.ListCreateAPIView):
    serializer_class = ElectionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_ec_member or self.request.user.is_staff:
            return Election.objects.all()
        return Election.objects.filter(status__in=["upcoming", "active", "completed"]) 

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

    # perform partial updates
    def perform_update(self, serializer):
        print('updating...')
        if not (self.request.user.is_ec_member or self.request.user.is_staff):
            raise permissions.PermissionDenied("Only EC members can update elections")
        serializer.save(created_by=self.request.user)


@cast_vote_schema
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def cast_vote(request):
    if not request.user.can_vote:
        return Response(
            {"error": "Cannot participate in this election"},
            status=status.HTTP_403_FORBIDDEN,
        )
    # Support bulk ballot payload: { election_id, selections: [{position_id, candidate_id}, ...] }
    if isinstance(request.data, dict) and "selections" in request.data:
        bulk_ser = BulkCastVoteSerializer(data=request.data)
        if not bulk_ser.is_valid():
            return Response(bulk_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        election = bulk_ser.validated_data["election"]
        items = bulk_ser.validated_data["validated_items"]

        # Enforce one vote per position per voter (anonymized check), and do all atomically
        created_votes = []
        with transaction.atomic():
            for item in items:
                position = item["position"]
                candidate = item["candidate"]
                approve = item.get("approve", True)

                # Duplicate check per position
                if Vote.has_voter_voted_for_position(request.user, position):
                    raise transaction.TransactionManagementError(
                        f"Already voted for position {position.title}"
                    )

                v = Vote.create_secure_vote(
                    voter=request.user,
                    candidate=candidate,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    approve=approve,
                )
                created_votes.append((v, position, candidate, approve))

            # Audit logs and session update once per election
            for v, position, candidate, approve in created_votes:
                AuditLog.objects.create(
                    action="vote_cast",
                    user=request.user,
                    resource_type="vote",
                    resource_id=str(v.id),
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    details={
                        "election_id": str(position.election.id),
                        "position_id": str(position.id),
                        "candidate_id": str(candidate.id),
                        "approve": bool(approve),
                        "encrypted": bool(v.encrypted_vote_data),
                        "verified": v.integrity_verified,
                    },
                )

            # Update or create session for this election
            try:
                session = VotingSession.objects.get(
                    user=request.user, election=election, session_end__isnull=True
                )
                session.votes_cast += len(created_votes)
                session.save()
            except VotingSession.DoesNotExist:
                VotingSession.objects.create(
                    user=request.user,
                    election=election,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    votes_cast=len(created_votes),
                )

        return Response(
            {
                "message": "Ballot submitted successfully",
                "count": len(created_votes),
            },
            status=status.HTTP_201_CREATED,
        )

    # Legacy single-position vote support
    serializer = CastVoteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    position = serializer.validated_data["position"]
    candidate = serializer.validated_data["candidate"]

    if Vote.has_voter_voted_for_position(request.user, position):
        return Response(
            {"error": "You have already voted for this position"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        vote = Vote.create_secure_vote(
            voter=request.user,
            candidate=candidate,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        AuditLog.objects.create(
            action="vote_cast",
            user=request.user,
            resource_type="vote",
            resource_id=str(vote.id),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            details={
                "election_id": str(position.election.id),
                "position_id": str(position.id),
                "candidate_id": str(candidate.id),
                "encrypted": bool(vote.encrypted_vote_data),
                "verified": vote.integrity_verified,
            },
        )

        try:
            session = VotingSession.objects.get(
                user=request.user, election=position.election, session_end__isnull=True
            )
            session.votes_cast += 1
            session.save()
        except VotingSession.DoesNotExist:
            VotingSession.objects.create(
                user=request.user,
                election=position.election,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                votes_cast=1,
            )

    return Response(
        {
            "message": "Vote cast successfully",
            "verified": vote.integrity_verified,
            "timestamp": vote.timestamp,
        },
        status=status.HTTP_201_CREATED,
    )

import secrets
@election_results_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def election_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    # Permissions: voters see only when published; EC can review after completion but before publish
    can_view = False
    if getattr(election, "results_published", False):
        can_view = True
    elif request.user.is_ec_member or request.user.is_staff:
        can_view = election.status == "completed"
    elif election.show_results_after_voting and election.status in ["active", "completed"]:
        try:
            can_view = Vote.has_user_voted_in_election(request.user, election)
        except Exception:
            can_view = False

    if not can_view:
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
                    "name": candidate.user.display_name,
                    "student_id": candidate.user.student_id,
                    "vote_count": candidate.vote_count,
                    "vote_percentage": candidate.vote_percentage,
                    "profile_picture_url": absolute_media_url_builder(request, candidate.profile_picture.url) if getattr(candidate, "profile_picture", None) else None,
                }
            )

        # If single-candidate position, compute yes/no breakdown
        yes_count = 0
        no_count = 0
        if position.candidates.count() == 1:
            # Iterate all votes for this position and inspect approve flag
            from .crypto import VotingCrypto
            crypto = VotingCrypto()
            for v in Vote.objects.filter(position_id=position.id):
                try:
                    data = crypto.decrypt_vote_data(v.encrypted_vote_data)
                    if data.get("approve") is False:
                        no_count += 1
                    else:
                        yes_count += 1
                except Exception:
                    continue

        # Sort by vote count descending
        candidates_with_votes.sort(key=lambda x: x["vote_count"], reverse=True)

        positions_with_results.append(
            {
                "id": position.id,
                "title": position.title,
                "total_votes": position.total_votes,
                "candidates": candidates_with_votes,
                **({"yes_count": yes_count, "no_count": no_count} if position.candidates.count() == 1 else {}),
            }
        )

    # Compute eligibility and turnout
    total_eligible_voters = User.objects.filter(is_active=True).count()
    total_votes_cast = election.total_votes
    total_unique_voters = election.total_voters
    voter_turnout = (total_unique_voters / total_eligible_voters * 100) if total_eligible_voters else 0

    # Persist summary for admins
    try:
        if request.user.is_ec_member or request.user.is_staff:
            ElectionResult.objects.update_or_create(
                election=election,
                defaults={
                    "total_eligible_voters": total_eligible_voters,
                    "total_votes_cast": total_votes_cast,
                    "voter_turnout_percentage": voter_turnout,
                    "generated_by": request.user,
                },
            )
    except Exception:
        pass

    return Response(
        {
            "election": {
                "id": str(election.id),
                "title": election.title,
                "status": election.status,
                "results_published": getattr(election, "results_published", False),
                "results_published_at": getattr(election, "results_published_at", None),
                "start_date": election.start_date,
                "end_date": election.end_date,
                "can_review_results": bool((request.user.is_ec_member or request.user.is_staff) and election.status == "completed" and not getattr(election, "results_published", False)),
                "can_archive": bool((request.user.is_ec_member or request.user.is_staff) and election.status == "completed" and getattr(election, "results_published", False)),
                "total_votes": total_votes_cast,
                "total_voters": total_unique_voters,
                "total_eligible_voters": total_eligible_voters,
                "voter_turnout_percentage": voter_turnout,
            },
            "positions": positions_with_results,
        }
    )

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def publish_election_results(request, election_id):
    """Admin publishes results after election is completed; triggers SMS to voters."""
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response({"error": "Only EC members can publish results"}, status=status.HTTP_403_FORBIDDEN)

    election = get_object_or_404(Election, id=election_id)
    if election.status != "completed":
        return Response({"error": "Election must be completed before publishing"}, status=status.HTTP_400_BAD_REQUEST)
    if getattr(election, "results_published", False):
        return Response({"message": "Results already published"})

    election.results_published = True
    election.results_published_at = timezone.now()
    election.save(update_fields=["results_published", "results_published_at"])

    # Notify voters via SMS (best effort)
    try:
        from accounts.models import User
        from utils.tasks import send_bulk_results_published_sms_task
        voter_ids = list(User.objects.filter(is_active=True).values_list("id", flat=True))
        if voter_ids:
            send_bulk_results_published_sms_task.delay(str(election.id), voter_ids)
    except Exception:
        pass

    return Response({"message": "Results published"})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def archive_election(request, election_id):
    """Admin archives an election after results are published. Voters won't see archived in lists."""
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response({"error": "Only EC members can archive elections"}, status=status.HTTP_403_FORBIDDEN)

    election = get_object_or_404(Election, id=election_id)
    if election.status != "completed":
        return Response({"error": "Only completed elections can be archived"}, status=status.HTTP_400_BAD_REQUEST)
    if not getattr(election, "results_published", False):
        return Response({"error": "Publish results before archiving"}, status=status.HTTP_400_BAD_REQUEST)

    election.status = "archived"
    election.save(update_fields=["status"])

    return Response({"message": "Election archived"})




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
    parser_classes = (MultiPartParser, FormParser)

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
        user_id = self.request.data.get("user")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            candidate_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404)

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

    # Intentionally minimal; add more aggregates as needed

    stats = {
        "total_elections": Election.objects.count(),
        "active_elections": Election.objects.filter(status="active").count(),
        "upcoming_elections": Election.objects.filter(status="upcoming").count(),
        "completed_elections": Election.objects.filter(status="completed").count(),
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
    # Reserved for future filters
    year_of_study = request.GET.get("year_of_study")
    search = request.GET.get("search")

    # Start with all users
    queryset = User.objects.all()

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


# Security-related views
@security_status_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def security_status(request, election_id):
    """
    Get security status and configuration for an election
    """

    election = get_object_or_404(Election, id=election_id)

    # Check if user can view security status
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response(
            {"error": "Only EC members can view security status"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Get or create security configuration
    security_config, created = ElectionSecurity.objects.get_or_create(
        election=election,
        defaults={
            "enable_vote_encryption": True,
            "enable_digital_signatures": True,
            "enable_audit_logging": True,
            "enable_ip_verification": True,
        },
    )

    # Check overall security configuration
    config_checks = check_security_configuration()

    # Get voting statistics
    total_votes = Vote.objects.filter(election_id=election.id).count()
    secure_votes = (
        Vote.objects.filter(election_id=election.id)
        .exclude(encrypted_vote_data="")
        .count()
    )
    verified_votes = Vote.objects.filter(
        election_id=election.id,
        integrity_verified=True,
        signature_verified=True,
    ).count()

    # Get audit logs
    recent_audits = AuditLog.objects.filter(
        resource_type="vote", details__election_id=str(election.id)
    ).count()

    return Response(
        {
            "election_id": str(election.id),
            "election_title": election.title,
            "security_configuration": {
                "vote_encryption_enabled": security_config.enable_vote_encryption,
                "digital_signatures_enabled": security_config.enable_digital_signatures,
                "audit_logging_enabled": security_config.enable_audit_logging,
                "ip_verification_enabled": security_config.enable_ip_verification,
                "two_factor_required": security_config.require_two_factor_auth,
            },
            "system_security": config_checks,
            "voting_statistics": {
                "total_votes": total_votes,
                "secure_votes": secure_votes,
                "verified_votes": verified_votes,
                "encryption_rate": (
                    (secure_votes / total_votes * 100) if total_votes > 0 else 0
                ),
                "verification_rate": (
                    (verified_votes / secure_votes * 100) if secure_votes > 0 else 0
                ),
            },
            "audit_trail": {
                "total_audit_entries": recent_audits,
            },
            "status": "secure" if all(config_checks.values()) else "needs_attention",
        }
    )


@verify_vote_integrity_schema
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def verify_vote_integrity(request, vote_id):
    """
    Verify the integrity of a specific vote
    """

    # Only EC members and staff can verify votes
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response(
            {"error": "Only EC members can verify vote integrity"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        vote = Vote.objects.get(id=vote_id)
    except Vote.DoesNotExist:
        return Response({"error": "Vote not found"}, status=status.HTTP_404)

    # Perform integrity verification
    is_valid = vote.verify_integrity()

    # Create audit log for verification
    AuditLog.objects.create(
        action="vote_verified",
        user=request.user,
        resource_type="vote",
        resource_id=str(vote.id),
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        details={
            "verification_result": is_valid,
            "integrity_verified": vote.integrity_verified,
            "signature_verified": vote.signature_verified,
        },
    )

    return Response(
        {
            "vote_id": str(vote.id),
            "is_valid": is_valid,
            "integrity_verified": vote.integrity_verified,
            "signature_verified": vote.signature_verified,
            "timestamp": vote.timestamp,
            "verification_performed_by": request.user.display_name,
            "verification_timestamp": timezone.now(),
        }
    )


@audit_trail_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def audit_trail(request, election_id):
    """
    Get audit trail for an election
    """

    election = get_object_or_404(Election, id=election_id)

    # Only EC members and staff can view audit trails
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response(
            {"error": "Only EC members can view audit trails"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Get audit logs for this election
    audit_logs = AuditLog.objects.filter(
        details__election_id=str(election.id)
    ).order_by("-timestamp")[
        :100
    ]  # Latest 100 entries

    # Format audit data
    audit_data = []
    for log in audit_logs:
        audit_data.append(
            {
                "id": str(log.id),
                "timestamp": log.timestamp,
                "action": log.action,
                "user": log.user.display_name if log.user else "System",
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "details": log.details,
                "integrity_hash": log.integrity_hash,
            }
        )

    return Response(
        {
            "election_id": str(election.id),
            "election_title": election.title,
            "audit_trail": audit_data,
            "total_entries": audit_logs.count(),
            "generated_at": timezone.now(),
            "generated_by": request.user.display_name,
        }
    )


@suspicious_activity_schema
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def suspicious_activity(request):
    """
    Get report of suspicious voting activities
    """

    # Only EC members and staff can view suspicious activity
    if not (request.user.is_ec_member or request.user.is_staff):
        return Response(
            {"error": "Only EC members can view suspicious activity reports"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Get suspicious voting sessions
    suspicious_sessions = VotingSession.objects.filter(is_suspicious=True).order_by(
        "-session_start"
    )[:50]

    # Format suspicious activity data
    activity_data = []
    for session in suspicious_sessions:
        activity_data.append(
            {
                "session_id": str(session.id),
                "user": session.user.display_name,
                "election": session.election.title,
                "session_start": session.session_start,
                "session_end": session.session_end,
                "ip_address": session.ip_address,
                "votes_cast": session.votes_cast,
                "suspicious_reason": session.suspicious_reason,
                "country_code": session.country_code,
                "city": session.city,
            }
        )

    return Response(
        {
            "suspicious_activities": activity_data,
            "total_suspicious_sessions": len(activity_data),
            "generated_at": timezone.now(),
            "generated_by": request.user.display_name,
        }
    )
