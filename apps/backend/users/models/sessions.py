from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.model_mixins import UUIDPrimaryKeyMixin, CreatedAtMixin

User = get_user_model()


class UserSession(UUIDPrimaryKeyMixin,
                  CreatedAtMixin,
                  models.Model):
    """
    This model is used to add a layer of index,
    so that user can find all their sessions conveniently.

    This model does not replace Django's default Session model,
    and should not be used for authentication and authorization.
    However, user can use this model as an entry point
    to delete their sessions.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_sessions',
        verbose_name=_("user"),
        help_text=_("The user of the session"),
    )
    session_key = models.CharField(
        max_length=40, unique=True,
        verbose_name=_("session key"),
        help_text=_("The session's session key"),
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("user agent"),
        help_text=_("The session's user agent"),
    )
    browser = models.CharField(
        blank=True, max_length=100,
        verbose_name=_("browser"),
        help_text=_("The session's browser"),
    )
    os = models.CharField(
        blank=True, max_length=100,
        verbose_name=_("operating system"),
        help_text=_("The session's operating system"),
    )
    device = models.CharField(
        blank=True, max_length=100,
        verbose_name=_("device"),
        help_text=_("The session's device"),
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name=_("IP address"),
        help_text=_("The session's IP address"),
    )
    last_accessed_at = models.DateField(
        verbose_name=_("last accessed at"),
        help_text=_("The session's last accessed Date"),
    )

    class Meta:
        verbose_name = _("user session")
        verbose_name_plural = _("user sessions")

        ordering = ['-created_at']
