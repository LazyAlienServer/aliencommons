from django.db import IntegrityError, transaction
from django.conf import settings
from bookmarks.models import Bookmark, BookmarkFolder
from core.tests.factories import (
    create_bookmark,
    create_bookmark_folder,
    create_article_publication,
    create_article,
    create_user,
)
from core.tests.testcases import BaseTestCase


class BookmarkModelTests(BaseTestCase):
    def setUp(self):
        self.user = create_user(username="reader")

    def test_user_factory_creates_default_bookmark_folder(self):
        self.assertTrue(
            BookmarkFolder.objects.filter(
                user=self.user,
                name=settings.DEFAULT_BOOKMARK_FOLDER_NAME,
            ).exists()
        )

    def test_bookmark_folder_string_representation_is_name(self):
        folder = create_bookmark_folder(user=self.user, name="Research")

        self.assertEqual(str(folder), "Research")

    def test_bookmark_string_representation_references_user_and_article(self):
        article = create_article(title="Guide")
        published = create_article_publication(article, title=article.source.title)
        bookmark = create_bookmark(self.user, published)

        self.assertEqual(
            str(bookmark),
            f"{self.user} bookmarked Publication of article Guide",
        )

    def test_bookmark_folder_rejects_duplicate_name_per_user(self):
        create_bookmark_folder(user=self.user, name="Research")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_bookmark_folder(user=self.user, name="Research")

    def test_bookmark_rejects_duplicate_article_publication_per_user(self):
        article = create_article()
        published = create_article_publication(article)
        create_bookmark(self.user, published)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_bookmark(self.user, published)

    def test_bookmark_folder_delete_removes_bookmarks(self):
        article = create_article()
        published = create_article_publication(article)
        folder = create_bookmark_folder(user=self.user)
        bookmark = create_bookmark(self.user, published, folder=folder)
        folder_id = folder.id

        folder.delete()

        self.assertFalse(BookmarkFolder.objects.filter(id=folder_id).exists())
        self.assertFalse(Bookmark.objects.filter(id=bookmark.id).exists())
