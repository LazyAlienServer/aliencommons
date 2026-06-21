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
        ARTICLE_PUBLICATION = 1, "Article Publication"
        COMMENT = 2, "Comment"
        COMMUNITY_POST = 3, "Community Post"

    target_type = models.IntegerField(
        choices=TargetType.choices,
        db_index=True,
        verbose_name=_("target type"),
        help_text=_("The type of object this content target points to"),
    )
    article_publication = models.OneToOneField(
        "articles.ArticlePublication",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="content_target",
        verbose_name=_("article publication"),
        help_text=_("The article publication this content target points to"),
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
    community_post = models.OneToOneField(
        "posts.CommunityPost",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="content_target",
        verbose_name=_("community post"),
        help_text=_("The community post this content target points to"),
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
                        article_publication__isnull=False,
                        comment__isnull=True,
                        community_post__isnull=True,
                    )
                    | models.Q(
                        target_type=2,
                        article_publication__isnull=True,
                        comment__isnull=False,
                        community_post__isnull=True,
                    )
                    | models.Q(
                        target_type=3,
                        article_publication__isnull=True,
                        comment__isnull=True,
                        community_post__isnull=False,
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
