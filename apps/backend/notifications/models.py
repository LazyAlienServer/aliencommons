from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import TimeStampedMixin, UUIDPrimaryKeyMixin


class NotificationEvent(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    class EventType(models.IntegerChoices):
        MENTION = 1, _("mention")
        COMMENT_REPLY = 2, _("comment reply")
        NEW_SUBSCRIBER = 3, _("new subscriber")
        SUBSCRIBED_AUTHOR_POSTED = 4, _("subscribed author posted")

    class DeliveryStatus(models.IntegerChoices):
        PENDING = 1, _("pending")
        PROCESSING = 2, _("processing")
        DELIVERED = 3, _("delivered")
        FAILED = 4, _("failed")

    event_type = models.IntegerField(choices=EventType.choices, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_events",
    )
    target = models.ForeignKey(
        "core.ContentTarget",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_events",
    )
    data = models.JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=255, unique=True)
    delivery_status = models.IntegerField(
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        db_index=True,
    )
    delivery_attempts = models.PositiveIntegerField(default=0)
    delivered_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["delivery_status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} event {self.id}"


class NotificationDelivery(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    event = models.ForeignKey(
        NotificationEvent,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_deliveries",
    )
    read_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "recipient"],
                name="unique_notification_event_delivery_recipient",
            ),
        ]
        indexes = [
            models.Index(fields=["recipient", "read_at", "created_at"]),
        ]

    def __str__(self):
        return f"Notification {self.event_id} for {self.recipient_id}"

