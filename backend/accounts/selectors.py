from operator import is_
from .models import User


def get_all_users():
    """Get all users ordered by date joined"""
    return User.objects.filter(is_active=True).order_by("-date_joined")


def get_user_by_id(user_id):
    """Get a user by their ID"""
    try:
        return User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None
