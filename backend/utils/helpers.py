import secrets
import string


def _generate_password(length: int = 10) -> str:
    """Generate a secure random password"""
    # Use letters, digits, and some safe punctuation
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))
