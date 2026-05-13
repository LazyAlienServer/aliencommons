from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import TimeStampedMixin, UUIDPrimaryKeyMixin


class Notification(UUIDPrimaryKeyMixin,
                   TimeStampedMixin,
                   models.Model):
    class NotificationType(models.TextChoices):
        MENTION = "mention", "Mention"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("recipient"),
        help_text=_("The user who receives the notification"),
    )

    actor_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="notification_actor",
        verbose_name=_("actor content type"),
        help_text=_("The content type of the actor"),
    )
    actor_object_id = models.UUIDField(
        verbose_name=_("actor object ID"),
        help_text=_("The UUID of the actor object"),
    )
    actor = GenericForeignKey(
        "actor_content_type",
        "actor_object_id",
    )

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notification_target",
        verbose_name=_("target content type"),
        help_text=_("The content type of the target"),
    )
    target_object_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_("target object ID"),
        help_text=_("The UUID of the target object"),
    )
    target = GenericForeignKey(
        "target_content_type",
        "target_object_id",
    )

    action_object_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notification_action_object",
        verbose_name=_("action object content type"),
        help_text=_("The content type of the action object"),
    )
    action_object_object_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_("action object ID"),
        help_text=_("The UUID of the action object"),
    )
    action_object = GenericForeignKey(
        "action_object_content_type",
        "action_object_object_id",
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        verbose_name=_("notification type"),
        help_text=_("The type of notification"),
    )
    verb = models.CharField(
        max_length=255,
        verbose_name=_("verb"),
        help_text=_("The action verb describing what happened"),
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("is read"),
        help_text=_("Whether the notification has been read"),
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("data"),
        help_text=_("Additional data for the notification"),
    )
    dedupe_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name=_("dedupe key"),
        help_text=_("Unique key to prevent duplicate notifications"),
    )

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "notification_type"]),
            models.Index(fields=["recipient", "created_at"]),
        ]

    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient}"
