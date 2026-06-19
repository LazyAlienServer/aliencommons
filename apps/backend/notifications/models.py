from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import TimeStampedMixin, UUIDPrimaryKeyMixin


class NotificationEvent(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    class Reason(models.IntegerChoices):
        MENTION = 1, _("mention")
        REPLY = 2, _("reply")
        SYSTEM = 3, _("system")
        SUBSCRIPTION = 4, _("subscription")

    class Channel(models.IntegerChoices):
        MENTIONS = 1, _("mentions")
        COMMENTS = 2, _("comments")
        SYSTEM = 3, _("system")
        SUBSCRIPTIONS = 4, _("subscriptions")

    class DeliveryStatus(models.IntegerChoices):
        PENDING = 1, _("pending")
        PROCESSING = 2, _("processing")
        DELIVERED = 3, _("delivered")
        FAILED = 4, _("failed")

    reason = models.IntegerField(choices=Reason.choices, db_index=True)
    channel = models.IntegerField(choices=Channel.choices, db_index=True)
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
    payload = models.JSONField(default=dict, blank=True)
    recipients = models.JSONField(default=list, blank=True)
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
            models.Index(fields=["channel", "created_at"]),
            models.Index(fields=["reason", "created_at"]),
            models.Index(fields=["delivery_status", "created_at"]),
        ]

    @classmethod
    def channel_for_reason(cls, reason):
        reason = cls.Reason(reason)
        return {
            cls.Reason.MENTION: cls.Channel.MENTIONS,
            cls.Reason.REPLY: cls.Channel.COMMENTS,
            cls.Reason.SYSTEM: cls.Channel.SYSTEM,
            cls.Reason.SUBSCRIPTION: cls.Channel.SUBSCRIPTIONS,
        }[reason]

    def save(self, *args, **kwargs):
        self.channel = self.channel_for_reason(self.reason)
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "reason" in update_fields and "channel" not in update_fields:
            kwargs["update_fields"] = [*update_fields, "channel"]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_reason_display()} event {self.id}"


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
