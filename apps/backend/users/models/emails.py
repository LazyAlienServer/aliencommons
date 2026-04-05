from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.model_mixins import CreatedAtMixin, UUIDPrimaryKeyMixin

User = get_user_model()


class EmailAddress(UUIDPrimaryKeyMixin,
                   CreatedAtMixin,
                   models.Model):
    """
    This model extracts email information from the user model, Profile.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="related_emails",
        verbose_name=_("user"),
        help_text=_("The user of the email address"),
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_("email"),
        help_text=_("The email of the email address"),
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("verified"),
        help_text=_("Whether the email is verified"),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("primary"),
        help_text=_("Whether the email is the primary email of the user"),
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
