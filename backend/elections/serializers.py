from rest_framework import serializers
from .models import Election, Position, Candidate, Vote, ElectionResult
from accounts.serializers import UserSerializer


class CandidateSerializer(serializers.ModelSerializer):
    vote_count = serializers.ReadOnlyField()
    vote_percentage = serializers.ReadOnlyField()

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


class PositionSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField()

    class Meta:
        model = Position
        fields = "__all__"


class ElectionSerializer(serializers.ModelSerializer):
    positions = PositionSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField()
    total_voters = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    can_vote = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(
        source="created_by.display_name", read_only=True
    )

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
        data["positions"] = PositionSerializer(instance.positions.all(), many=True).data
        return data


class ElectionListSerializer(serializers.ModelSerializer):
    total_votes = serializers.ReadOnlyField()
    total_voters = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(
        source="created_by.display_name", read_only=True
    )

    class Meta:
        model = Election
        fields = (
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "total_votes",
            "total_voters",
            "is_active",
            "created_by_name",
            "created_at",
        )


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("candidate", "timestamp")
        read_only_fields = ("voter", "timestamp", "ip_address")


class CastVoteSerializer(serializers.Serializer):
    position_id = serializers.IntegerField()
    candidate_id = serializers.IntegerField()

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


class ElectionResultSerializer(serializers.ModelSerializer):
    election = ElectionSerializer(read_only=True)

    class Meta:
        model = ElectionResult
        fields = "__all__"
