from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, AcademicYear


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

        # Set admission year if not provided
        if not attrs.get("admission_year"):
            from datetime import datetime

            attrs["admission_year"] = datetime.now().year

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("Account is disabled")
            attrs["user"] = user
        else:
            raise serializers.ValidationError("Must include username and password")
        return attrs


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    can_vote = serializers.ReadOnlyField()
    has_paid_current_dues = serializers.ReadOnlyField()
    current_academic_year = serializers.ReadOnlyField()
    is_current_student = serializers.ReadOnlyField()
    years_since_admission = serializers.ReadOnlyField()

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
            "has_paid_current_dues",
            "is_ec_member",
            "display_name",
            "can_vote",
            "current_academic_year",
            "is_current_student",
            "years_since_admission",
        )
        read_only_fields = ("has_paid_current_dues", "is_ec_member")


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"
