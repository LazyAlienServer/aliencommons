from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import TimeStampedMixin, UUIDPrimaryKeyMixin


class BaseReport(UUIDPrimaryKeyMixin,
                 TimeStampedMixin,
                 models.Model):
    class ReportReason(models.IntegerChoices):
        SPAM = 1, "Spam"
        HARASSMENT = 2, "Harassment"
        HATE = 3, "Hate"
        SEXUAL_CONTENT = 4, "Sexual Content"
        VIOLENCE = 5, "Violence"
        ILLEGAL = 6, "Illegal"
        OTHER = 99, "Other"

    class ReportStatus(models.IntegerChoices):
        PENDING = 1, "Pending"
        REVIEWING = 2, "Reviewing"
        RESOLVED = 3, "Resolved"
        REJECTED = 4, "Rejected"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_reports",
        verbose_name=_("reporter"),
        help_text=_("The user who submitted the report"),
    )
    reason = models.IntegerField(
        choices=ReportReason.choices,
        verbose_name=_("reason"),
        help_text=_("The reason for the report"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("description"),
        help_text=_("The reporter's optional description"),
    )
    snapshot = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("snapshot"),
        help_text=_("The target state when the report was submitted"),
    )
    status = models.IntegerField(
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        db_index=True,
        verbose_name=_("status"),
        help_text=_("The review status of the report"),
    )
    resolution_note = models.TextField(
        blank=True,
        default="",
        verbose_name=_("resolution note"),
        help_text=_("Moderator note for the report resolution"),
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_%(class)s_reports",
        verbose_name=_("resolved by"),
        help_text=_("The moderator who last resolved or rejected the report"),
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("resolved at"),
        help_text=_("The DateTime when the report was resolved or rejected"),
    )

    class Meta:
        abstract = True


class ContentReport(BaseReport):
    target = models.ForeignKey(
        "core.ContentTarget",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_reports",
        verbose_name=_("target"),
        help_text=_("The content target being reported"),
    )
    target_type = models.IntegerField(
        verbose_name=_("target type"),
        help_text=_("The content target type at submission time"),
    )
    target_object_id = models.UUIDField(
        verbose_name=_("target object ID"),
        help_text=_("The reported object's ID at submission time"),
    )

    class Meta:
        verbose_name = _("content report")
        verbose_name_plural = _("content reports")

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reporter", "created_at"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["target_type", "target_object_id"]),
        ]

    def __str__(self):
        return f"Content report {self.id}"


class UserReport(BaseReport):
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports_received",
        verbose_name=_("reported user"),
        help_text=_("The user being reported"),
    )
    reported_user_id_snapshot = models.UUIDField(
        verbose_name=_("reported user ID snapshot"),
        help_text=_("The reported user's ID at submission time"),
    )

    class Meta:
        verbose_name = _("user report")
        verbose_name_plural = _("user reports")

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reporter", "created_at"]),
            models.Index(fields=["reported_user", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"User report {self.id}"

