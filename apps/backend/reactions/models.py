from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from articles.models import PublishedArticle
from core.model_mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class ReactionTarget(UUIDPrimaryKeyMixin,
                     CreatedAtMixin,
                     models.Model):
    """
    A strongly referenced target that can receive reactions.
    """
    class TargetType(models.IntegerChoices):
        PUBLISHED_ARTICLE = 1, "Published Article"

    target_type = models.IntegerField(
        choices=TargetType.choices,
        default=TargetType.PUBLISHED_ARTICLE,
        db_index=True,
        verbose_name=_("target type"),
        help_text=_("The type of object this reaction target points to"),
    )
    published_article = models.OneToOneField(
        PublishedArticle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reaction_target",
        verbose_name=_("published article"),
        help_text=_("The published article this reaction target points to"),
    )

    class Meta:
        verbose_name = _("reaction target")
        verbose_name_plural = _("reaction targets")

        ordering = ["-created_at"]
        constraints = [
            # TODO: When comment/community post targets are added, upgrade this
            # constraint so exactly one target object field is non-null and
            # matches target_type.
            models.CheckConstraint(
                condition=(
                    models.Q(
                        target_type=1,
                        published_article__isnull=False,
                    )
                ),
                name="reaction_target_requires_matching_object",
            ),
        ]
        indexes = [
            models.Index(fields=["target_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_target_type_display()} target {self.id}"


class Reaction(UUIDPrimaryKeyMixin,
               CreatedAtMixin,
               models.Model):
    """
    A user's current like/dislike state for a reaction target.
    """
    class ReactionType(models.IntegerChoices):
        LIKE = 1, "Like"
        DISLIKE = 2, "Dislike"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reactions",
        verbose_name=_("user"),
        help_text=_("The user who made the reaction"),
    )
    target = models.ForeignKey(
        ReactionTarget,
        on_delete=models.CASCADE,
        related_name="reactions",
        verbose_name=_("target"),
        help_text=_("The target being reacted to"),
    )
    reaction_type = models.IntegerField(
        choices=ReactionType.choices,
        verbose_name=_("reaction type"),
        help_text=_("The user's reaction type"),
    )

    class Meta:
        verbose_name = _("reaction")
        verbose_name_plural = _("reactions")

        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target"],
                name="unique_reaction_per_user_target",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["target", "reaction_type"]),
        ]

    def __str__(self):
        return f"{self.user} {self.get_reaction_type_display()} {self.target_id}"
