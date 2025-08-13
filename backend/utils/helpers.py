import secrets
import string
from rest_framework.request import HttpRequest
from django.contrib.auth import get_user_model

User = get_user_model()


def _generate_password(length: int = 10) -> str:
    """Generate a secure random password"""
    # Use letters and digits
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def _generate_username(
        first_name: str, last_name: str, student_id: str
    ) -> str:
        """Generate username from first name, last name, and student ID"""
        # Clean names
        first_clean = first_name.capitalize().replace(" ", "")
        last_clean = last_name.capitalize().replace(" ", "")

        # Try different username patterns
        patterns = [
            f"{first_clean}{last_clean[:2]}",
            f"{first_clean}{last_clean[:3]}",
            f"{first_clean}_{last_clean[:2]}",
            f"{first_clean}_{last_clean[:3]}",
            f"user{student_id}",
        ]

        for pattern in patterns:
            if not User.objects.filter(username=pattern).exists():
                return pattern

        # If all patterns exist, append a number
        base_username = patterns[0]
        counter = 1
        while User.objects.filter(username=f"{base_username}{counter}").exists():
            counter += 1

        return f"{base_username}{counter}"


def absolute_media_url_builder(request: HttpRequest, media_url: str):
    return request.build_absolute_uri(media_url)
