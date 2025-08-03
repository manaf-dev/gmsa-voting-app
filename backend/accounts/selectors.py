from .models import User


def get_all_users():
    """Get all users ordered by date joined"""
    return User.objects.all().order_by("-date_joined")


def get_user_by_id(user_id):
    """Get a user by their ID"""
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
