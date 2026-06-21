from django.urls import reverse
from django.conf import settings

from rest_framework import status

from bookmarks.models import Bookmark, BookmarkFolder
from core.tests.factories import (
    create_bookmark,
    create_bookmark_folder,
    create_article_publication,
    create_article,
    create_user,
)
from core.tests.testcases import BaseAPITestCase


class BookmarkViewTests(BaseAPITestCase):
    def setUp(self):
        self.user = create_user(username="reader")
        self.other_user = create_user(username="other-reader")
        self.folder = BookmarkFolder.objects.get(
            user=self.user,
            name=settings.DEFAULT_BOOKMARK_FOLDER_NAME,
        )
        self.other_folder = BookmarkFolder.objects.get(
            user=self.other_user,
            name=settings.DEFAULT_BOOKMARK_FOLDER_NAME,
        )
        self.article = create_article(title="Guide")
        self.published = create_article_publication(self.article, title=self.article.source.title)

    def test_user_can_create_bookmark_folder(self):
        self.authenticate(self.user)
        response = self.post_json(
            reverse("bookmark_folder-list"),
            {
                "name": "Research",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assertEqual(response.data["data"]["name"], "Research")
        self.assert_uuid_equal(response.data["data"]["user"], self.user.id)

    def test_user_only_lists_own_bookmark_folders(self):
        own_folder = create_bookmark_folder(user=self.user, name="Mine")
        create_bookmark_folder(user=self.other_user, name="Not mine")

        self.authenticate(self.user)
        response = self.get_json(reverse("bookmark_folder-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        folder_ids = {item["id"] for item in response.data["data"]["results"]}
        self.assertIn(str(self.folder.id), folder_ids)
        self.assertIn(str(own_folder.id), folder_ids)
        self.assertEqual(len(folder_ids), 2)

    def test_user_can_delete_folder_and_its_bookmarks(self):
        folder = create_bookmark_folder(user=self.user, name="To delete")
        bookmark = create_bookmark(self.user, self.published, folder=folder)
        folder_id = folder.id

        self.authenticate(self.user)
        response = self.delete_json(reverse("bookmark_folder-detail", args=[folder_id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="deleted",
        )
        self.assertFalse(BookmarkFolder.objects.filter(id=folder_id).exists())
        self.assertFalse(Bookmark.objects.filter(id=bookmark.id).exists())

    def test_user_can_create_bookmark_for_article_publication(self):
        self.authenticate(self.user)
        response = self.post_json(
            reverse("bookmark-list"),
            {
                "folder": str(self.folder.id),
                "article_publication": str(self.published.id),
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["user"], self.user.id)
        self.assert_uuid_equal(response.data["data"]["folder"], self.folder.id)
        self.assert_uuid_equal(response.data["data"]["article_publication"], self.published.id)
        self.assertEqual(Bookmark.objects.count(), 1)

    def test_bookmark_requires_folder(self):
        self.authenticate(self.user)
        response = self.post_json(
            reverse("bookmark-list"),
            {
                "article_publication": str(self.published.id),
            },
        )

        self.assert_error_response(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_user_cannot_bookmark_into_another_users_folder(self):
        self.authenticate(self.user)
        response = self.post_json(
            reverse("bookmark-list"),
            {
                "folder": str(self.other_folder.id),
                "article_publication": str(self.published.id),
            },
        )

        self.assert_error_response(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_user_cannot_duplicate_bookmark(self):
        create_bookmark(self.user, self.published, folder=self.folder)

        self.authenticate(self.user)
        response = self.post_json(
            reverse("bookmark-list"),
            {
                "folder": str(self.folder.id),
                "article_publication": str(self.published.id),
            },
        )

        self.assert_error_response(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(Bookmark.objects.count(), 1)

    def test_user_can_move_bookmark_to_another_folder(self):
        target_folder = create_bookmark_folder(user=self.user, name="Later")
        bookmark = create_bookmark(self.user, self.published, folder=self.folder)

        self.authenticate(self.user)
        response = self.patch_json(
            reverse("bookmark-detail", args=[bookmark.id]),
            {
                "folder": str(target_folder.id),
            },
        )

        bookmark.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="updated",
        )
        self.assertEqual(bookmark.folder, target_folder)

    def test_user_only_lists_own_bookmarks(self):
        own_bookmark = create_bookmark(self.user, self.published, folder=self.folder)
        other_article = create_article(title="Other")
        other_published = create_article_publication(other_article, title=other_article.source.title)
        create_bookmark(self.other_user, other_published, folder=self.other_folder)

        self.authenticate(self.user)
        response = self.get_json(reverse("bookmark-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assert_uuid_equal(response.data["data"]["results"][0]["id"], own_bookmark.id)

    def test_user_can_filter_bookmarks_by_folder(self):
        own_bookmark = create_bookmark(self.user, self.published, folder=self.folder)
        other_folder = create_bookmark_folder(user=self.user, name="Other")
        other_article = create_article(title="Other")
        other_published = create_article_publication(other_article, title=other_article.source.title)
        create_bookmark(self.user, other_published, folder=other_folder)

        self.authenticate(self.user)
        response = self.get_json(
            reverse("bookmark-list"),
            {
                "folder": str(self.folder.id),
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assert_uuid_equal(response.data["data"]["results"][0]["id"], own_bookmark.id)
