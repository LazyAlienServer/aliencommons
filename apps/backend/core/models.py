from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class ContentTarget(UUIDPrimaryKeyMixin,
                    CreatedAtMixin,
                    models.Model):
    """
    A strongly referenced target that can receive comments and reactions.
    """
    class TargetType(models.IntegerChoices):
        PUBLISHED_ARTICLE = 1, "Published Article"
        COMMENT = 2, "Comment"

    target_type = models.IntegerField(
        choices=TargetType.choices,
        db_index=True,
        verbose_name=_("target type"),
        help_text=_("The type of object this content target points to"),
    )
    published_article = models.OneToOneField(
        "articles.PublishedArticle",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="content_target",
        verbose_name=_("published article"),
        help_text=_("The published article this content target points to"),
    )
    comment = models.OneToOneField(
        "comments.Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="content_target",
        verbose_name=_("comment"),
        help_text=_("The comment this content target points to"),
    )

    class Meta:
        verbose_name = _("content target")
        verbose_name_plural = _("content targets")

        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        target_type=1,
                        published_article__isnull=False,
                        comment__isnull=True,
                    )
                    | models.Q(
                        target_type=2,
                        published_article__isnull=True,
                        comment__isnull=False,
                    )
                ),
                name="content_target_requires_exactly_one_object",
            ),
        ]
        indexes = [
            models.Index(fields=["target_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_target_type_display()} target {self.id}"
