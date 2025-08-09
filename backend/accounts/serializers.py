from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, AcademicYear


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "student_id",
            "phone_number",
            "year_of_study",
            "program",
            "admission_year",
            "password",
            "confirm_password",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords don't match")

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Username or Student ID for login")
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            # The custom StudentIDBackend will handle both username and student_id authentication
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    "Invalid credentials. Please check your username/student ID and password."
                )
            if not user.is_active:
                raise serializers.ValidationError("Account is disabled.")
            attrs["user"] = user
        else:
            raise serializers.ValidationError("Must include username and password.")
        return attrs


class UserSerializer(serializers.ModelSerializer):
    active_elections_vote_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "student_id",
            "phone_number",
            "year_of_study",
            "program",
            "admission_year",
            "is_ec_member",
            "created_at",
            "updated_at",
            "can_vote",
            "active_elections_vote_status",
        )

    def get_active_elections_vote_status(self, obj) -> dict:
        try:
            from elections.models import Vote
            return Vote.get_user_active_election_vote_map(obj)
        except Exception:
            return {}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["display_name"] = instance.display_name
        representation["is_current_student"] = instance.is_current_student
        representation["years_since_admission"] = instance.years_since_admission
        return representation


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"
