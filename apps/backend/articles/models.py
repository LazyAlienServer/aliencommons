from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.model_mixins import TimeStampedMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


User = get_user_model()


class SourceArticle(UUIDPrimaryKeyMixin,
                    TimeStampedMixin,
                    SoftDeleteMixin,
                    models.Model):
    """
    Model for all articles
    Mixin fields:
    - created_at
    - updated_at
    - id
    - is_deleted
    """

    class ArticleStatus(models.IntegerChoices):
        """
        4 different source article status
        """
        DRAFT = 0, "Draft"
        PENDING = 1, "Pending"
        PUBLISHED = 2, "Published"
        UNPUBLISHED = 3, "Unpublished"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="source_articles",
        verbose_name=_("author"),
        help_text=_("The author of the article"),
    )
    title = models.CharField(
        max_length=60, db_index=True, default="",
        verbose_name=_("title"),
        help_text=_("The title of the article"),
    )
    content = models.JSONField(
        blank=True, default=dict,
        verbose_name=_("content"),
        help_text=_("The content of the article"),
    )
    status = models.IntegerField(
        choices=ArticleStatus.choices, default=ArticleStatus.DRAFT, db_index=True,
        verbose_name=_("status"),
        help_text=_("The status of the article"),
    )
    last_moderation_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("last moderation at"),
        help_text=_("The last moderation DateTime of the article"),
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
        SourceArticle, on_delete=models.CASCADE, related_name="published_version",
        verbose_name=_("source article"),
        help_text=_("The source article of the published version"),
    )
    title = models.CharField(
        max_length=60, db_index=True, default="",
        verbose_name=_("title"),
        help_text=_("The title of the published article"),
    )
    content = models.JSONField(
        blank=True, default=dict,
        verbose_name=_("content"),
        help_text=_("The content of the published article"),
    )

    class Meta:
        verbose_name = _("published article")
        verbose_name_plural = _("published articles")

        ordering = ['-created_at']

    def __str__(self):
        return f"Published version of article {self.source_article}"


class ArticleSnapshot(UUIDPrimaryKeyMixin, models.Model):
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
        SourceArticle, on_delete=models.CASCADE, related_name="article_snapshots",
        verbose_name=_("source article"),
        help_text=_("The source article of the article snapshot"),
    )
    title = models.CharField(
        max_length=60, db_index=True, default="",
        verbose_name=_("title"),
        help_text=_("The title of the article snapshot"),
    )
    content = models.JSONField(
        blank=True, default=dict,
        verbose_name=_("content"),
        help_text=_("The content of the article snapshot"),
    )
    content_hash = models.CharField(
        max_length=64, blank=True, default="", db_index=True,
        verbose_name=_("content hash"),
        help_text=_("The content hash of the article snapshot"),
    )
    moderation_status = models.IntegerField(
        choices=SnapshotStatus.choices, default=SnapshotStatus.PENDING, db_index=True,
        verbose_name=_("moderation status"),
        help_text=_("The moderation status of the article snapshot"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, editable=False,
        verbose_name=_("created at"),
        help_text=_("The created DateTime of the article snapshot"),
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


class ArticleEvent(UUIDPrimaryKeyMixin, models.Model):
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
        SourceArticle, on_delete=models.CASCADE, related_name="article_events",
        verbose_name=_("source articles"),
        help_text=_("The source article of the article event"),
    )
    article_snapshot = models.ForeignKey(
        ArticleSnapshot, on_delete=models.SET_NULL, null=True, related_name="article_events",
        verbose_name=_("snapshot"),
        help_text=_("The article snapshot of the article event"),
    )
    annotation = models.TextField(
        null=True, blank=True,
        verbose_name=_("annotation"),
        help_text=_("The annotation of the article event"),
    )
    event_type = models.IntegerField(
        choices=EventType.choices,
        verbose_name=_("event type"),
        help_text=_("The event type of the article event"),
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="article_events",
        verbose_name=_("actor"),
        help_text=_("The actor of the article event"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, editable=False,
        verbose_name=_("created at"),
        help_text=_("The created DateTime of the article event"),
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
