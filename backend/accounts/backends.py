from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class StudentIDBackend(ModelBackend):
    """
    Custom authentication backend that allows login with either username or student_id.

    This backend supports:
    - Login with username (default Django behavior)
    - Login with student_id
    - Case-insensitive matching for both fields
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        if username is None or password is None:
            return None

        try:
            # Try to find user by username or student_id (case-insensitive)
            user = User.objects.get(
                Q(username__iexact=username) | Q(student_id__iexact=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # If there are multiple users with similar usernames/student_ids,
            # try exact match first
            try:
                user = User.objects.get(Q(username=username) | Q(student_id=username))
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
