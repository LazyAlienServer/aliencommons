from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.model_mixins import TimeStampedMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin, CreatedAtMixin


User = get_user_model()


class Article(UUIDPrimaryKeyMixin,
              TimeStampedMixin,
              SoftDeleteMixin,
              models.Model):
    """
    Stable article identity and workflow state.

    Mixin fields:
    - created_at
    - updated_at
    - id
    - is_deleted
    """
    class ArticleStatus(models.IntegerChoices):
        DRAFT = 0, "Draft"
        PENDING = 1, "Pending"
        PUBLISHED = 2, "Published"
        UNPUBLISHED = 3, "Unpublished"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="articles",
        verbose_name=_("author"),
        help_text=_("The author of the article"),
    )
    status = models.IntegerField(
        choices=ArticleStatus.choices, default=ArticleStatus.DRAFT, db_index=True,
        verbose_name=_("status"),
        help_text=_("The status of the article"),
    )
    last_saved_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("last saved at"),
        help_text=_("The last saved DateTime of the article"),
    )
    last_moderation_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("last moderation at"),
        help_text=_("The last moderation DateTime of the article"),
    )

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['author', 'status', 'updated_at'])
        ]

    def __str__(self):
        return self.source.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_deleted:
            ArticlePublication.objects.filter(article=self).delete()


class ArticleSource(UUIDPrimaryKeyMixin,
                    TimeStampedMixin,
                    models.Model):
    """
    Current editable source content for an article.

    Mixin fields:
    - id
    - created_at
    - updated_at
    """
    default_title = "Untitled"
    default_markdown = "# Untitled"

    article = models.OneToOneField(
        Article, on_delete=models.CASCADE, related_name="source",
        verbose_name=_("article"),
        help_text=_("The article this source content belongs to"),
    )
    title = models.CharField(
        max_length=100, db_index=True, blank=True, default=default_title,
        verbose_name=_("title"),
        help_text=_("The current source title of the article"),
    )
    markdown = models.TextField(
        blank=True, default=default_markdown,
        verbose_name=_("article in markdown"),
        help_text=_("The current article in Markdown format"),
    )
    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_("version"),
        help_text=_("The current draft version of the article source"),
    )

    class Meta:
        verbose_name = _("article source")
        verbose_name_plural = _("article sources")

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title', 'created_at']),
        ]

    def __str__(self):
        return self.title


class ArticlePublication(UUIDPrimaryKeyMixin,
                         TimeStampedMixin,
                         models.Model):
    """
    Current public reading projection of an approved article snapshot.

    Mixin fields:
    - id
    - created_at
    - updated_at
    """
    article = models.OneToOneField(
        Article, on_delete=models.CASCADE, related_name="publication",
        verbose_name=_("article"),
        help_text=_("The article of the publication"),
    )
    approved_snapshot = models.ForeignKey(
        "ArticleSnapshot", on_delete=models.CASCADE, related_name="publications",
        verbose_name=_("approved snapshot"),
        help_text=_("The approved snapshot used to render this publication"),
    )
    title = models.CharField(
        max_length=100, db_index=True,
        verbose_name=_("title"),
        help_text=_("The title of the article publication"),
    )
    html = models.TextField(
        verbose_name=_("article in html"),
        help_text=_("The article in HTML format"),
    )
    publication_at = models.DateTimeField(
        db_index=True,
        verbose_name=_("published at"),
        help_text=_("The DateTime of publication of the article publication"),
    )

    class Meta:
        verbose_name = _("article publication")
        verbose_name_plural = _("article publications")

        ordering = ['-created_at']

    def __str__(self):
        return f"Publication of article {self.article}"


class ArticleSnapshot(UUIDPrimaryKeyMixin,
                      CreatedAtMixin,
                      models.Model):
    """
    Freeze the current version of the article for review and retrospection.

    Mixin fields:
        - id
        - created_at
    """

    class SnapshotStatus(models.IntegerChoices):
        PENDING = 1, "Pending"
        WITHDRAWN = 2, "Withdrawn"
        APPROVED = 3, "Approved"
        REJECTED = 4, "Rejected"

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="article_snapshots",
        verbose_name=_("article"),
        help_text=_("The article of the article snapshot"),
    )
    title = models.CharField(
        max_length=100, db_index=True,
        verbose_name=_("title"),
        help_text=_("The title of the article snapshot"),
    )
    markdown = models.TextField(
        verbose_name=_("article in markdown"),
        help_text=_("The article in Markdown format"),
    )
    hash = models.CharField(
        max_length=64, default="", db_index=True,
        verbose_name=_("hash"),
        help_text=_("The hash value of the article snapshot"),
    )
    source_version = models.PositiveIntegerField(
        verbose_name=_("source version"),
        help_text=_("The source version of the article snapshot"),
    )
    moderation_status = models.IntegerField(
        choices=SnapshotStatus.choices, default=SnapshotStatus.PENDING, db_index=True,
        verbose_name=_("moderation status"),
        help_text=_("The moderation status of the article snapshot"),
    )

    class Meta:
        verbose_name = _("article snapshot")
        verbose_name_plural = _("article snapshots")

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['moderation_status', 'created_at']),
            models.Index(fields=['article', 'hash']),
        ]

    def __str__(self):
        return f"Snapshot of article {self.article_id}"


class ArticleEvent(UUIDPrimaryKeyMixin,
                   CreatedAtMixin,
                   models.Model):
    """
    Record events related to articles

    Mixin fields:
        - id
        - created_at
    """

    class EventType(models.IntegerChoices):
        CREATE = 0, "Create"
        SUBMIT = 1, "Submit"
        WITHDRAW = 2, "Withdraw"
        APPROVE = 3, "Approve"
        REJECT = 4, "Reject"
        UNPUBLISH = 5, "Unpublish"
        DELETE = 6, "Delete"

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="article_events",
        verbose_name=_("article"),
        help_text=_("The article of the article event"),
    )
    article_snapshot = models.ForeignKey(
        ArticleSnapshot, on_delete=models.SET_NULL, null=True, related_name="article_events",
        verbose_name=_("snapshot"),
        help_text=_("The article snapshot of the article event"),
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

    class Meta:
        verbose_name = _("article event")
        verbose_name_plural = _("article events")

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['actor', 'created_at']),
            models.Index(fields=['article_snapshot', 'created_at']),
            models.Index(fields=['event_type', 'created_at']),
        ]

    def __str__(self):
        return (
            f"Operation {self.get_event_type_display()} "
            f"by {self.actor_id} "
            f"on article {self.article_id}"
        )
