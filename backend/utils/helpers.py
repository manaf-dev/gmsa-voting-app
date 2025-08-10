import secrets
import string
from rest_framework.request import HttpRequest


def _generate_password(length: int = 10) -> str:
    """Generate a secure random password"""
    # Use letters, digits, and some safe punctuation
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


def absolute_media_url_builder(request: HttpRequest, media_url: str):
    return request.build_absolute_uri(media_url)
