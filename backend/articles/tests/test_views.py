from django.urls import reverse

from rest_framework import status

from core.tests.factories import (
    create_article_snapshot,
    create_moderator,
    create_published_article,
    create_source_article,
    create_user,
)
from core.tests.testcases import BaseAPITestCase
from articles.models import (
    ArticleEvent,
    ArticleSnapshot,
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
                "content": {"type": "doc", "content": [{"type": "paragraph"}]},
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
            message="created",
        )
        self.assertEqual(response.data["data"]["title"], "Draft title")
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

    def test_approve_endpoint_requires_moderator(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        create_article_snapshot(article)

        self.authenticate(self.author)
        response = self.post_json(
            reverse("source_article-approve", args=[article.id]),
            {"annotation": "looks good"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(PublishedArticle.objects.filter(source_article=article).exists())
        self.assertEqual(ArticleEvent.objects.filter(source_article=article).count(), 0)

    def test_moderator_can_approve_pending_article(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        snapshot = create_article_snapshot(article)

        self.authenticate(self.moderator)
        response = self.post_json(
            reverse("source_article-approve", args=[article.id]),
            {"annotation": "approved"},
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
