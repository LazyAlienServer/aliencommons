from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class UserSubscription(UUIDPrimaryKeyMixin,
                       CreatedAtMixin,
                       models.Model):
    """
    A user subscribing to another user.
    """
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions",
        verbose_name=_("subscriber"),
        help_text=_("The user who subscribes"),
    )
    subscribed_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscribers",
        verbose_name=_("subscribed to"),
        help_text=_("The user being subscribed to"),
    )

    class Meta:
        verbose_name = _("user subscription")
        verbose_name_plural = _("user subscriptions")

        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "subscribed_to"],
                name="unique_user_subscription",
            ),
            models.CheckConstraint(
                condition=~models.Q(subscriber=models.F("subscribed_to")),
                name="prevent_self_subscription",
            ),
        ]
        indexes = [
            models.Index(fields=["subscriber", "created_at"]),
            models.Index(fields=["subscribed_to", "created_at"]),
        ]

    def __str__(self):
        return f"{self.subscriber} subscribes to {self.subscribed_to}"
