from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import SoftDeleteMixin, TimeStampedMixin, UUIDPrimaryKeyMixin


class Comment(UUIDPrimaryKeyMixin,
              TimeStampedMixin,
              SoftDeleteMixin,
              models.Model):
    """
    A user's comment on a content target.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments",
        verbose_name=_("author"),
        help_text=_("The author of the comment"),
    )
    target = models.ForeignKey(
        "core.ContentTarget",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("target"),
        help_text=_("The content target this comment belongs to"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("parent"),
        help_text=_("The parent comment this comment replies to"),
    )
    body = models.TextField(
        verbose_name=_("body"),
        help_text=_("The comment body"),
    )

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["target", "created_at"]),
            models.Index(fields=["parent", "created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["is_deleted", "created_at"]),
        ]

    def __str__(self):
        return f"Comment {self.id} by {self.author_id}"

