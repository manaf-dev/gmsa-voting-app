from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Election, Position, Candidate, Vote, ElectionResult
from accounts.serializers import UserSerializer
from utils.helpers import absolute_media_url_builder

class CandidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["position"] = {
            "id": instance.position.id,
            "title": instance.position.title,
            "description": instance.position.description,
            "order": instance.position.order,
        }
        data["user"] = UserSerializer(instance.user).data
        data["vote_count"] = instance.vote_count
        data["vote_percentage"] = instance.vote_percentage
        # Add absolute URL for profile picture if present
        try:
            if instance.profile_picture:
                req = self.context.get("request") if hasattr(self, "context") else None
                data["profile_picture_url"] = absolute_media_url_builder(req, instance.profile_picture.url)
        except Exception:
            pass
        return data


class PositionSerializer(serializers.ModelSerializer):

    @extend_schema_field(serializers.IntegerField)
    def get_total_votes(self, obj):
        return obj.total_votes

    class Meta:
        model = Position
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["candidates"] = CandidateSerializer(
            instance.candidates.all(), many=True, context=self.context
        ).data
        data["total_votes"] = instance.total_votes
        return data


class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = "__all__"


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["created_by"] = {
            "id": instance.created_by.id,
            "display_name": instance.created_by.display_name,
            "email": instance.created_by.email,
        }
        data["positions"] = PositionSerializer(instance.positions.all(), many=True, context=self.context).data
        data["is_active"] = instance.is_active
        data["can_vote"] = instance.can_vote
        # Results publishing flags and derived permissions
        data["results_published"] = getattr(instance, "results_published", False)
        data["results_published_at"] = getattr(instance, "results_published_at", None)
        request = self.context.get("request") if hasattr(self, "context") else None
        user = getattr(request, "user", None)
        # Candidate spotlight flag
        try:
            from .models import Candidate as Cand
            data["is_candidate"] = bool(user and user.is_authenticated and Cand.objects.filter(position__election=instance, user=user).exists())
        except Exception:
            data["is_candidate"] = False
        can_review = bool(getattr(user, "is_ec_member", False) and instance.status == "completed" and not data["results_published"])
        data["can_review_results"] = can_review
        data["can_archive"] = bool((getattr(user, "is_ec_member", False) or getattr(user, "is_staff", False)) and instance.status == "completed" and data["results_published"]) 
        user_voted = False
        try:
            if user and user.is_authenticated:
                from .models import Vote
                user_voted = Vote.has_user_voted_in_election(user, instance)
        except Exception:
            user_voted = False
        data["can_view_results"] = bool(
            data["results_published"]
            or (getattr(user, "is_ec_member", False) and instance.status == "completed")
            or (instance.show_results_after_voting and instance.status in ["active", "completed"] and user_voted)
        )
        return data


class ElectionListSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()
    results_published = serializers.ReadOnlyField()
    can_view_results = serializers.SerializerMethodField()
    is_candidate = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(
        source="created_by.display_name", read_only=True
    )

    @extend_schema_field(serializers.BooleanField)
    def get_is_active(self, obj):
        return obj.is_active

    class Meta:
        model = Election
        fields = (
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "is_active",
            "results_published",
            "can_view_results",
            "is_candidate",
            "created_by_name",
            "created_at",
        )

    def get_can_view_results(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        user = getattr(request, "user", None)
        user_voted = False
        try:
            if user and user.is_authenticated:
                from .models import Vote
                user_voted = Vote.has_user_voted_in_election(user, obj)
        except Exception:
            user_voted = False
        return bool(
            getattr(obj, "results_published", False)
            or (getattr(user, "is_ec_member", False) and obj.status == "completed")
            or (obj.show_results_after_voting and obj.status in ["active", "completed"] and user_voted)
        )

    def get_is_candidate(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        user = getattr(request, "user", None)
        try:
            from .models import Candidate as Cand
            return bool(user and user.is_authenticated and Cand.objects.filter(position__election=obj, user=user).exists())
        except Exception:
            return False


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("candidate", "timestamp")
        read_only_fields = ("voter", "timestamp", "ip_address")


class CastVoteSerializer(serializers.Serializer):
    position_id = serializers.UUIDField()
    candidate_id = serializers.UUIDField()

    def validate(self, attrs):
        position_id = attrs.get("position_id")
        candidate_id = attrs.get("candidate_id")

        try:
            position = Position.objects.get(id=position_id)
            candidate = Candidate.objects.get(id=candidate_id, position=position)
        except (Position.DoesNotExist, Candidate.DoesNotExist):
            raise serializers.ValidationError("Invalid position or candidate")

        # Check if election is active
        if not position.election.can_vote:
            raise serializers.ValidationError("This election is not currently active")

        attrs["position"] = position
        attrs["candidate"] = candidate
        return attrs


class SelectionItemSerializer(serializers.Serializer):
    position_id = serializers.UUIDField()
    candidate_id = serializers.UUIDField(required=False)
    approve = serializers.BooleanField(required=False, help_text="For single-candidate positions, set True for YES, False for NO")


class BulkCastVoteSerializer(serializers.Serializer):
    election_id = serializers.UUIDField()
    selections = SelectionItemSerializer(many=True)

    def validate(self, attrs):
        election_id = attrs.get("election_id")
        selections = attrs.get("selections") or []

        # Validate election
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise serializers.ValidationError("Invalid election")

        if not election.can_vote:
            raise serializers.ValidationError("This election is not currently active")

        if not selections:
            raise serializers.ValidationError("No selections provided")

        # Collect validated objects and enforce constraints
        validated_items = []
        seen_positions = set()

        for item in selections:
            pid = item.get("position_id")
            cid = item.get("candidate_id")
            approve = item.get("approve", None)

            try:
                position = Position.objects.get(id=pid)
            except Position.DoesNotExist:
                raise serializers.ValidationError(f"Invalid position: {pid}")

            if position.election_id != election.id:
                raise serializers.ValidationError(
                    f"Position {position.id} does not belong to this election"
                )

            # If position has single candidate, we can allow approve flag without explicit candidate_id
            candidates_qs = Candidate.objects.filter(position=position).order_by("order")
            if cid is None and approve is not None and candidates_qs.count() == 1:
                candidate = candidates_qs.first()
            else:
                try:
                    candidate = Candidate.objects.get(id=cid, position=position)
                except Candidate.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Invalid candidate {cid} for position {position.id}"
                    )

            # Only one choice per position (model enforces 1 vote per position)
            if position.id in seen_positions:
                raise serializers.ValidationError(
                    f"Multiple selections for the same position are not allowed ({position.title})"
                )
            seen_positions.add(position.id)

            # For multi-candidate positions, approve shouldn't be set
            if candidates_qs.count() > 1 and approve is not None:
                raise serializers.ValidationError(
                    f"'approve' is only valid for single-candidate positions ({position.title})"
                )

            validated_items.append({
                "position": position,
                "candidate": candidate,
                "approve": approve if approve is not None else True,
            })

        attrs["election"] = election
        attrs["validated_items"] = validated_items
        return attrs


class ElectionResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElectionResult
        fields = "__all__"

    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["election"] = ElectionSerializer(instance.election).data
        return data
