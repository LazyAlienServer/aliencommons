from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import SoftDeleteMixin, TimeStampedMixin, UUIDPrimaryKeyMixin


class CommunityPost(UUIDPrimaryKeyMixin,
                    TimeStampedMixin,
                    SoftDeleteMixin,
                    models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="community_posts",
        verbose_name=_("author"),
        help_text=_("The author of the post"),
    )
    body = models.TextField(
        verbose_name=_("body"),
        help_text=_("The post body"),
    )
    mentions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("mentions"),
        help_text=_("Ordered user IDs referenced by mention tokens in the post body"),
    )

    class Meta:
        verbose_name = _("community post")
        verbose_name_plural = _("community posts")

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["is_deleted", "created_at"]),
        ]

    def __str__(self):
        return f"Post {self.id} by {self.author_id}"
