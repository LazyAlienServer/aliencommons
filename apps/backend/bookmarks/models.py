from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from articles.models import ArticlePublication
from core.model_mixins import CreatedAtMixin, TimeStampedMixin, UUIDPrimaryKeyMixin


class BookmarkFolder(UUIDPrimaryKeyMixin,
                     TimeStampedMixin,
                     models.Model):
    """
    A single-level folder for a user's article bookmarks.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmark_folders",
        verbose_name=_("user"),
        help_text=_("The user who owns the bookmark folder"),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
        help_text=_("The name of the bookmark folder"),
    )

    class Meta:
        verbose_name = _("bookmark folder")
        verbose_name_plural = _("bookmark folders")

        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_bookmark_folder_name_per_user",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return self.name


class Bookmark(UUIDPrimaryKeyMixin,
               CreatedAtMixin,
               models.Model):
    """
    A user's bookmark for one article publication.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="article_bookmarks",
        verbose_name=_("user"),
        help_text=_("The user who owns the bookmark"),
    )
    folder = models.ForeignKey(
        BookmarkFolder, on_delete=models.CASCADE, related_name="bookmarks",
        verbose_name=_("folder"),
        help_text=_("The folder that contains the bookmark"),
    )
    article_publication = models.ForeignKey(
        ArticlePublication, on_delete=models.CASCADE, related_name="bookmarks",
        verbose_name=_("article publication"),
        help_text=_("The article publication being bookmarked"),
    )

    class Meta:
        verbose_name = _("bookmark")
        verbose_name_plural = _("bookmarks")

        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "article_publication"],
                name="unique_bookmark_article_publication_per_user",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["folder", "created_at"]),
            models.Index(fields=["article_publication", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} bookmarked {self.article_publication}"
