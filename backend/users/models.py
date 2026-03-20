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

from core.models.mixins import UUIDPrimaryKeyMixin


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

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Used by Django `createsuperuser`.
        Keep it here to avoid breaking the management command.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have 'is_staff=True'.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have 'is_superuser=True'.")

        user = self.create_user(username=username, password=password, **extra_fields)

        email = self.normalize_email(email)
        EmailAddress.objects.create(
            user=user,
            email=email,
            is_verified=False,
            is_primary=True
        )

        return user


class User(UUIDPrimaryKeyMixin,
           AbstractUser):
    """
    The User model, inherits from AbstractUser.
    'email' field, 'first_name' field and 'last_name' field are set to None.
    Emails are separately managed by 'EmailAddress' Model.
    """
    default_signature = "This player is somewhat mysterious..."

    username = models.CharField(
        verbose_name=_("username"),
        max_length=30, unique=True
    )
    avatar = models.ImageField(
        verbose_name=_("avatar"),
        upload_to=avatar_upload_to, blank=True, null=True, storage=AvatarStorage()
    )
    signature = models.CharField(
        verbose_name=_("signature"),
        max_length=60, blank=True, default=default_signature,
    )
    is_moderator = models.BooleanField(
        verbose_name= _("moderator status"),
        default=False
    )
    is_email_verified = models.BooleanField(
        verbose_name=_("email verified"),
        default=False
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


class EmailAddress(UUIDPrimaryKeyMixin,
                   models.Model):
    """
    This model extracts email information from the user model, Profile.
    """
    user = models.ForeignKey(
        verbose_name=_("user"),
        to=User, on_delete=models.CASCADE, related_name="related_emails"
    )
    email = models.EmailField(
        verbose_name=_("email"),
        unique=True
    )
    is_verified = models.BooleanField(
        verbose_name=_("verified"),
        default=False
    )
    is_primary = models.BooleanField(
        verbose_name=_("primary"),
        default=False
    )
    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        auto_now_add=True, db_index=True, editable=False
    )

    class Meta:
        verbose_name = _("email")
        verbose_name_plural = _("emails")

        # One user can only have one primary email
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_primary=True),
                name='unique_user_primary_emails'
            ),
        ]

    def __str__(self):
        return self.email
