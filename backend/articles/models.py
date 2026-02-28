from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


User = get_user_model()


class SourceArticle(UUIDPrimaryKeyMixin,
                    TimeStampedMixin,
                    SoftDeleteMixin,
                    models.Model):
    """
    Model for all articles

    Local fields:
        - author
        - title
        - content
        - last_moderation_at
        - status

    Mixin fields:
        - created_at
        - updated_at
        - id
        - is_deleted
    """

    class ArticleStatus(models.IntegerChoices):
        """
        5 different article status
        """
        DRAFT = 0, "Draft"
        PENDING = 1, "Pending"
        PUBLISHED = 2, "Published"
        REJECTED = 3, "Rejected"
        UNPUBLISHED = 4, "Unpublished"
        DELETED = 5, "Deleted"

    author = models.ForeignKey(
        verbose_name=_("author"),
        to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="source_articles"
    )
    title = models.CharField(
        verbose_name=_("title"),
        max_length=60, db_index=True, default=""
    )
    content = models.JSONField(
        verbose_name=_("content"),
        blank=True, default=dict
    )
    status = models.IntegerField(
        verbose_name=_("status"),
        choices=ArticleStatus.choices, default=ArticleStatus.DRAFT, db_index=True
    )
    last_moderation_at = models.DateTimeField(
        verbose_name=_("last moderation at"),
        blank=True, null=True
    )

    class Meta:
        verbose_name = _("source article")
        verbose_name_plural = _("source articles")

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return self.title


class PublishedArticle(UUIDPrimaryKeyMixin,
                       TimeStampedMixin,
                       models.Model):
    """
    Mixin fields:
    - id
    - created_at
    - updated_at
    """

    source_article = models.OneToOneField(
        verbose_name=_("source article"),
        to=SourceArticle, on_delete=models.CASCADE, related_name="published_version"
    )
    title = models.CharField(
        verbose_name=_("title"),
        max_length=60, db_index=True, default=""
    )
    content = models.JSONField(
        verbose_name=_("content"),
        blank=True, default=dict
    )

    class Meta:
        verbose_name = _("published article")
        verbose_name_plural = _("published articles")

        ordering = ['-created_at']

    def __str__(self):
        return f"Published version of article {self.source_article}"


class ArticleSnapshot(UUIDPrimaryKeyMixin,
                      models.Model):
    """
    Freeze the current version of the article for review and retrospection.

    Mixin fields:
        - id
    """

    class SnapshotStatus(models.IntegerChoices):
        PENDING = 1, "Pending"
        WITHDRAWN = 2, "Withdrawn"
        APPROVED = 3, "Approved"
        REJECTED = 4, "Rejected"

    source_article = models.ForeignKey(
        verbose_name=_("source article"),
        to=SourceArticle, on_delete=models.CASCADE, related_name="article_snapshots"
    )
    title = models.CharField(
        verbose_name=_("title"),
        max_length=60, db_index=True, default=""
    )
    content = models.JSONField(
        verbose_name=_("content"),
        blank=True, default=dict
    )
    content_hash = models.CharField(
        verbose_name=_("content hash"),
        max_length=64, blank=True, default="", db_index=True
    )
    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        default=timezone.now, db_index=True, editable=False
    )
    moderation_status = models.IntegerField(
        verbose_name=_("moderation status"),
        choices=SnapshotStatus.choices, default=SnapshotStatus.PENDING, db_index=True
    )

    class Meta:
        verbose_name = _("article snapshot")
        verbose_name_plural = _("article snapshots")

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_article', 'created_at']),
            models.Index(fields=['moderation_status', 'created_at']),
            models.Index(fields=['source_article', 'content_hash']),
        ]

    def __str__(self):
        return f"Snapshot of article {self.source_article_id}"


class ArticleEvent(UUIDPrimaryKeyMixin,
                   models.Model):
    """
    Record events related to articles

    Mixin fields:
        - id
    """

    class EventType(models.IntegerChoices):
        SUBMIT = 1, "Submit"
        WITHDRAW = 2, "Withdraw"
        APPROVE = 3, "Approve"
        REJECT = 4, "Reject"
        UNPUBLISH = 5, "Unpublish"
        DELETE = 6, "Delete"

    source_article = models.ForeignKey(
        verbose_name=_("source articles"),
        to=SourceArticle, on_delete=models.CASCADE, related_name="article_events"
    )
    article_snapshot = models.ForeignKey(
        verbose_name=_("snapshot"),
        to=ArticleSnapshot, on_delete=models.SET_NULL, null=True, related_name="related_events"
    )
    annotation = models.TextField(
        verbose_name=_("annotation"),
        null=True, blank=True
    )
    event_type = models.IntegerField(
        verbose_name=_("event type"),
        choices=EventType.choices
    )
    actor = models.ForeignKey(
        verbose_name=_("actor"),
        to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="article_events_actors"
    )
    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        default=timezone.now, db_index=True, editable=False
    )

    class Meta:
        verbose_name = _("article event")
        verbose_name_plural = _("article events")

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_article', 'created_at']),
            models.Index(fields=['actor', 'created_at']),
            models.Index(fields=['article_snapshot', 'created_at']),
            models.Index(fields=['event_type', 'created_at']),
        ]

    def __str__(self):
        return (
            f"Operation {self.get_event_type_display()} "
            f"by {self.actor_id} "
            f"on article {self.source_article_id}"
        )
