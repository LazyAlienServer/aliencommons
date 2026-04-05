from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from .models import EmailAddress
from .utils import normalize_email

User = get_user_model()


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return None

        email = normalize_email(email)
        try:
            email_address = EmailAddress.objects.get(email=email)
            if not email_address.is_verified:
                return None
        except EmailAddress.DoesNotExist:
            return None

        user = email_address.user

        if user.check_password(password) and user.is_active:
            return user

    @staticmethod
    def user_can_authenticate(user):
        """
        Reject users with is_active=False.
        """
        return user.is_active

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None
