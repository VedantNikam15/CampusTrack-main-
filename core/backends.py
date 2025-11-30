from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """Authenticate with either email or username (case-insensitive).

    This backend tries to find a user whose email OR username matches the
    supplied `username` parameter (case-insensitive). If found, it verifies
    the password and returns the user if valid.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
        except UserModel.DoesNotExist:
            return None

        # Use ModelBackend's helper to check active/staff and password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
