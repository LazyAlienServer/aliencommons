from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import filepath_to_uri
from django.conf import settings
from django.utils.translation import gettext_lazy as _

import uuid
from pathlib import Path
from urllib.parse import urljoin

from core.model_mixins import UUIDPrimaryKeyMixin


def avatar_upload_to(instance):
    return str(Path("avatars") / str(instance.username) / f"{uuid.uuid4().hex}.webp")


class AvatarStorage(FileSystemStorage):
    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        url = filepath_to_uri(name)
        if url is not None:
            url = url.lstrip("/")

        if name.startswith("default_avatar/"):
            return urljoin(settings.STATIC_URL, url)
        return urljoin(self.base_url, url)


class ProfileManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password, **extra_fields):
        """
        Lowest-level user creation.
        EmailAddress is not created here.
        """
        if not username:
            raise ValueError('Username field must be filled')
        if not password:
            raise ValueError("Password must be set")

        username = username.strip()
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Used by Django `createsuperuser`.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have 'is_staff=True'.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have 'is_superuser=True'.")

        user = self.create_user(username=username, password=password, **extra_fields)

        return user


class User(UUIDPrimaryKeyMixin,
           AbstractUser):
    """
    The User model, inherits from AbstractUser.
    'email' field, 'first_name' field and 'last_name' field are set to None.
    Emails are separately managed by 'EmailAddress' Model.

    Hidden Fields declared in AbstractUser and AbstractBaseUser:
    - password
    - last_login
    - is_active
    - is_anonymous (@property)
    - is_authenticated (@property)
    - is_staff
    - date_joined

    Always select set 'is_active' to False instead of deleting a user directly.
    """
    default_signature = "This player is somewhat mysterious..."

    username = models.CharField(
        max_length=30, unique=True,
        verbose_name=_("username"),
        help_text=_("The username of the user"),
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_to, blank=True, null=True, storage=AvatarStorage(),
        verbose_name=_("avatar"),
        help_text=_("The avatar of the user")
    )
    signature = models.CharField(
        max_length=60, blank=True, default=default_signature,
        verbose_name=_("signature"),
        help_text=_("The signature of the user")
    )
    is_moderator = models.BooleanField(
        default=False,
        verbose_name=_("moderator status"),
        help_text=_("Whether the user is a moderator")
    )
    is_email_verified = models.BooleanField(
        default=False, editable=False,
        verbose_name=_("email verified"),
        help_text=_("Whether at least an email of the user is verified")
    )

    email = None
    first_name = None
    last_name = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = ProfileManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username
