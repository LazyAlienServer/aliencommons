from django.urls import reverse

from rest_framework import status
from unittest.mock import patch

from core.tests.factories import (
    create_article_snapshot,
    create_collection,
    create_collection_item,
    create_moderator,
    create_published_article,
    create_source_article,
    create_user,
)
from core.tests.testcases import BaseAPITestCase
from articles.models import (
    ArticleEvent,
    ArticleSnapshot,
    Collection,
    CollectionItem,
    PublishedArticle,
    SourceArticle,
)


class ArticleViewTests(BaseAPITestCase):
    def setUp(self):
        self.author = create_user(username="author")
        self.other_author = create_user(username="other-author")
        self.moderator = create_moderator(username="moderator")

    def test_create_source_article_returns_formatted_response(self):
        self.authenticate(self.author)
        response = self.post_json(
            reverse("source_article-list"),
            {
                "title": "Draft title",
                "markdown": "Hello from Markdown",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
            message="created",
        )
        self.assertEqual(response.data["data"]["title"], "Draft title")
        self.assertEqual(response.data["data"]["markdown"], "Hello from Markdown")
        self.assert_uuid_equal(response.data["data"]["author"], self.author.id)
        self.assertEqual(SourceArticle.objects.count(), 1)

    def test_source_article_list_only_returns_articles_owned_by_authenticated_author(self):
        own_article = create_source_article(author=self.author, title="Mine")
        other_article = create_source_article(
            author=self.other_author,
            title="Not mine",
        )
        create_article_snapshot(own_article)
        create_published_article(own_article)
        create_article_snapshot(other_article)

        self.authenticate(self.author)
        response = self.get_json(reverse("source_article-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
            message="listed",
        )
        self.assertEqual(response.data["data"]["count"], 1)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assert_uuid_equal(response.data["data"]["results"][0]["id"], own_article.id)
        self.assert_uuid_equal(
            response.data["data"]["results"][0]["last_snapshot_id"],
            ArticleSnapshot.objects.get(source_article=own_article).id,
        )
        self.assert_uuid_equal(
            response.data["data"]["results"][0]["published_version_id"],
            PublishedArticle.objects.get(source_article=own_article).id,
        )

    def test_retrieve_source_article_returns_404_for_non_author(self):
        article = create_source_article(author=self.author)

        self.authenticate(self.other_author)
        response = self.get_json(reverse("source_article-detail", args=[article.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_can_save_draft_source_article(self):
        article = create_source_article(
            author=self.author,
            title="Old title",
            markdown="Old Markdown",
        )

        self.authenticate(self.author)
        response = self.patch_json(
            reverse("source_article-detail", args=[article.id]),
            {
                "title": "New title",
                "markdown": "New Markdown",
            },
        )

        article.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="saved",
            message="saved",
        )
        self.assertEqual(response.data["data"]["title"], "New title")
        self.assertEqual(response.data["data"]["markdown"], "New Markdown")
        self.assertEqual(response.data["data"]["version"], 2)
        self.assertIsNotNone(response.data["data"]["last_saved_at"])
        self.assertEqual(article.version, 2)
        self.assertIsNotNone(article.last_saved_at)

    def test_author_cannot_save_pending_source_article(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        create_article_snapshot(article)

        self.authenticate(self.author)
        response = self.patch_json(
            reverse("source_article-detail", args=[article.id]),
            {
                "markdown": "Edited while pending",
            },
        )

        article.refresh_from_db()
        self.assert_error_response(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="state_transition_error",
        )
        self.assertEqual(article.markdown, "Hello")
        self.assertEqual(article.version, 1)

    def test_approve_endpoint_requires_moderator(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        create_article_snapshot(article)

        self.authenticate(self.author)
        response = self.post_json(
            reverse("source_article-approve", args=[article.id]),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(PublishedArticle.objects.filter(source_article=article).exists())
        self.assertEqual(ArticleEvent.objects.filter(source_article=article).count(), 0)

    @patch("articles.services.articles.render_md_to_html", return_value="<p>Hello</p>")
    def test_moderator_can_approve_pending_article(self, render_mock):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        snapshot = create_article_snapshot(article)

        self.authenticate(self.moderator)
        response = self.post_json(
            reverse("source_article-approve", args=[article.id]),
        )

        article.refresh_from_db()
        snapshot.refresh_from_db()

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="approved",
        )
        self.assertEqual(response.data["data"]["event_type"], ArticleEvent.EventType.APPROVE)
        self.assert_uuid_equal(response.data["data"]["article_snapshot_id"], snapshot.id)
        self.assertEqual(article.status, SourceArticle.ArticleStatus.PUBLISHED)
        self.assertEqual(
            snapshot.moderation_status,
            ArticleSnapshot.SnapshotStatus.APPROVED,
        )
        self.assertTrue(PublishedArticle.objects.filter(source_article=article).exists())
        render_mock.assert_called_once_with(snapshot.markdown)

    def test_pending_snapshots_endpoint_only_lists_pending_ones_for_moderator(self):
        pending_article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        rejected_article = create_source_article(
            author=self.other_author,
            status=SourceArticle.ArticleStatus.DRAFT,
            title="Rejected draft",
        )
        pending_snapshot = create_article_snapshot(pending_article)
        create_article_snapshot(
            rejected_article,
            moderation_status=ArticleSnapshot.SnapshotStatus.REJECTED,
        )

        self.authenticate(self.moderator)
        response = self.get_json(reverse("article_snapshot-pending-ones"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        self.assertEqual(len(response.data["data"]), 1)
        self.assert_uuid_equal(response.data["data"][0]["id"], pending_snapshot.id)

    def test_author_can_create_collection(self):
        self.authenticate(self.author)
        response = self.post_json(
            reverse("collection-list"),
            {
                "title": "Redstone playlist",
                "description": "A path through the basics",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assertEqual(response.data["data"]["title"], "Redstone playlist")
        self.assert_uuid_equal(response.data["data"]["author"], self.author.id)
        self.assertEqual(Collection.objects.count(), 1)

    def test_collections_are_readable_without_authentication(self):
        first_collection = create_collection(
            author=self.author,
            title="First playlist",
        )
        second_collection = create_collection(
            author=self.author,
            title="Second playlist",
        )

        response = self.get_json(reverse("collection-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        result_ids = {item["id"] for item in response.data["data"]["results"]}
        self.assertIn(str(first_collection.id), result_ids)
        self.assertIn(str(second_collection.id), result_ids)

    def test_non_author_cannot_update_collection(self):
        collection = create_collection(author=self.author)

        self.authenticate(self.other_author)
        response = self.patch_json(
            reverse("collection-detail", args=[collection.id]),
            {
                "title": "Not allowed",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        collection.refresh_from_db()
        self.assertNotEqual(collection.title, "Not allowed")

    def test_author_can_add_owned_article_to_collection(self):
        collection = create_collection(author=self.author)
        article = create_source_article(author=self.author)
        published = create_published_article(article)

        self.authenticate(self.author)
        response = self.post_json(
            reverse("collection_item-list"),
            {
                "collection": str(collection.id),
                "published_article": str(published.id),
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["collection"], collection.id)
        self.assert_uuid_equal(response.data["data"]["published_article"], published.id)
        self.assert_uuid_equal(response.data["data"]["source_article_id"], article.id)
        self.assertEqual(response.data["data"]["position"], 1)
        self.assertEqual(CollectionItem.objects.count(), 1)

    def test_author_cannot_add_another_authors_article_to_collection(self):
        collection = create_collection(author=self.author)
        article = create_source_article(author=self.other_author)
        published = create_published_article(article)

        self.authenticate(self.author)
        response = self.post_json(
            reverse("collection_item-list"),
            {
                "collection": str(collection.id),
                "published_article": str(published.id),
            },
        )

        self.assert_error_response(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(CollectionItem.objects.count(), 0)

    def test_author_can_delete_collection_and_its_items(self):
        collection = create_collection(author=self.author)
        article = create_source_article(author=self.author)
        published = create_published_article(article)
        create_collection_item(collection, published)
        collection_id = collection.id

        self.authenticate(self.author)
        response = self.delete_json(reverse("collection-detail", args=[collection_id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="deleted",
        )
        self.assertFalse(Collection.objects.filter(id=collection_id).exists())
        self.assertFalse(CollectionItem.objects.filter(collection_id=collection_id).exists())
