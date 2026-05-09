from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import ContentTarget
from core.model_mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


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
        ContentTarget,
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
