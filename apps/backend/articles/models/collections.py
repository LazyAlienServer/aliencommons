from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import CreatedAtMixin, TimeStampedMixin, UUIDPrimaryKeyMixin

from .articles import ArticlePublication


class Collection(UUIDPrimaryKeyMixin,
                 TimeStampedMixin,
                 models.Model):
    """
    A playlist-like grouping of an author's published articles.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="article_collections",
        verbose_name=_("author"),
        help_text=_("The author of the collection"),
    )
    title = models.CharField(
        max_length=100, db_index=True,
        verbose_name=_("title"),
        help_text=_("The title of the collection"),
    )
    description = models.TextField(
        blank=True, default="",
        verbose_name=_("description"),
        help_text=_("The description of the collection"),
    )

    class Meta:
        verbose_name = _("collection")
        verbose_name_plural = _("collections")

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["author", "created_at"]),
        ]

    def __str__(self):
        return self.title


class CollectionItem(UUIDPrimaryKeyMixin,
                     CreatedAtMixin,
                     models.Model):
    """
    One ordered published article inside a collection.
    """
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="items",
        verbose_name=_("collection"),
        help_text=_("The collection that contains this item"),
    )
    article_publication = models.ForeignKey(
        ArticlePublication, on_delete=models.CASCADE, related_name="collection_items",
        verbose_name=_("article publication"),
        help_text=_("The article publication in the collection"),
    )
    position = models.PositiveIntegerField(
        verbose_name=_("position"),
        help_text=_("The item's position in the collection"),
    )

    class Meta:
        verbose_name = _("collection item")
        verbose_name_plural = _("collection items")

        ordering = ["collection", "position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["collection", "article_publication"],
                name="unique_collection_article_publication",
            ),
            models.UniqueConstraint(
                fields=["collection", "position"],
                name="unique_collection_item_position",
            ),
        ]
        indexes = [
            models.Index(fields=["collection", "position"]),
            models.Index(fields=["article_publication", "created_at"]),
        ]

    def __str__(self):
        return f"{self.article_publication} in {self.collection}"
