from django.utils import timezone

from datetime import timedelta

from articles.models import (
    ArticleEvent,
    ArticleSnapshot,
    PublishedArticle,
    SourceArticle,
)
from articles.services.articles import (
    approve,
    reject,
    soft_delete,
    submit,
    unpublish,
    withdraw,
)
from core.exceptions import ServiceError
from core.tests.factories import (
    create_article_snapshot,
    create_moderator,
    create_published_article,
    create_source_article,
    create_user,
)
from core.tests.testcases import BaseTestCase


class ArticleServiceTests(BaseTestCase):
    def setUp(self):
        self.author = create_user(username="author")
        self.moderator = create_moderator(username="moderator")

    def assert_service_error(self, exc_context, *, code):
        self.assertEqual(exc_context.exception.code, code)

    def test_submit_creates_pending_snapshot_and_event(self):
        article = create_source_article(author=self.author)

        result = submit(source_article_id=article.id, actor=self.author)

        article.refresh_from_db()
        snapshot = ArticleSnapshot.objects.get(source_article=article)
        event = ArticleEvent.objects.get(source_article=article)

        self.assertEqual(article.status, SourceArticle.ArticleStatus.PENDING)
        self.assertEqual(snapshot.title, article.title)
        self.assertEqual(snapshot.content, article.content)
        self.assertEqual(
            snapshot.moderation_status,
            ArticleSnapshot.SnapshotStatus.PENDING,
        )
        self.assertEqual(event.event_type, ArticleEvent.EventType.SUBMIT)
        self.assertEqual(event.actor, self.author)
        self.assertEqual(result["event_id"], event.id)
        self.assertEqual(result["article_snapshot_id"], snapshot.id)

    def test_submit_rejects_unchanged_content_after_previous_snapshot(self):
        article = create_source_article(author=self.author)
        create_article_snapshot(article)

        with self.assertRaises(ServiceError) as exc:
            submit(source_article_id=article.id, actor=self.author)

        self.assert_service_error(exc, code="no_change_error")
        self.assertEqual(ArticleSnapshot.objects.filter(source_article=article).count(), 1)
        self.assertEqual(ArticleEvent.objects.filter(source_article=article).count(), 0)

    def test_submit_enforces_cooldown_after_moderation(self):
        article = create_source_article(
            author=self.author,
            last_moderation_at=timezone.now() - timedelta(hours=1),
        )

        with self.assertRaises(ServiceError) as exc:
            submit(source_article_id=article.id, actor=self.author)

        self.assert_service_error(exc, code="cooldown_error")

    def test_withdraw_restores_draft_and_marks_snapshot_withdrawn(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        snapshot = create_article_snapshot(article)

        result = withdraw(source_article_id=article.id, actor=self.author)

        article.refresh_from_db()
        snapshot.refresh_from_db()
        event = ArticleEvent.objects.get(source_article=article)

        self.assertEqual(article.status, SourceArticle.ArticleStatus.DRAFT)
        self.assertEqual(
            snapshot.moderation_status,
            ArticleSnapshot.SnapshotStatus.WITHDRAWN,
        )
        self.assertEqual(event.event_type, ArticleEvent.EventType.WITHDRAW)
        self.assertEqual(result["article_snapshot_id"], snapshot.id)

    def test_approve_creates_published_article_and_marks_snapshot_approved(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        snapshot = create_article_snapshot(article)

        result = approve(source_article_id=article.id, actor=self.moderator)

        article.refresh_from_db()
        snapshot.refresh_from_db()
        published = PublishedArticle.objects.get(source_article=article)
        event = ArticleEvent.objects.get(source_article=article)

        self.assertEqual(article.status, SourceArticle.ArticleStatus.PUBLISHED)
        self.assertIsNotNone(article.last_moderation_at)
        self.assertEqual(
            snapshot.moderation_status,
            ArticleSnapshot.SnapshotStatus.APPROVED,
        )
        self.assertEqual(published.title, snapshot.title)
        self.assertEqual(published.content, snapshot.content)
        self.assertEqual(event.event_type, ArticleEvent.EventType.APPROVE)
        self.assertEqual(result["event_id"], event.id)

    def test_approve_updates_existing_published_article(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
            title="Updated title",
            content={"blocks": [{"type": "paragraph", "text": "Updated"}]},
        )
        snapshot = create_article_snapshot(article)
        published = create_published_article(
            article,
            title="Old title",
            content={"blocks": [{"type": "paragraph", "text": "Old"}]},
        )

        approve(source_article_id=article.id, actor=self.moderator)

        published.refresh_from_db()
        self.assertEqual(PublishedArticle.objects.filter(source_article=article).count(), 1)
        self.assertEqual(published.id, PublishedArticle.objects.get(source_article=article).id)
        self.assertEqual(published.title, snapshot.title)
        self.assertEqual(published.content, snapshot.content)

    def test_reject_restores_draft_and_marks_snapshot_rejected(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )
        snapshot = create_article_snapshot(article)

        reject(source_article_id=article.id, actor=self.moderator)

        article.refresh_from_db()
        snapshot.refresh_from_db()
        event = ArticleEvent.objects.get(source_article=article)

        self.assertEqual(article.status, SourceArticle.ArticleStatus.DRAFT)
        self.assertIsNotNone(article.last_moderation_at)
        self.assertEqual(
            snapshot.moderation_status,
            ArticleSnapshot.SnapshotStatus.REJECTED,
        )
        self.assertEqual(event.event_type, ArticleEvent.EventType.REJECT)

    def test_unpublish_marks_article_unpublished(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PUBLISHED,
        )
        snapshot = create_article_snapshot(article)

        unpublish(source_article_id=article.id, actor=self.moderator)

        article.refresh_from_db()
        snapshot.refresh_from_db()
        event = ArticleEvent.objects.get(source_article=article)

        self.assertEqual(article.status, SourceArticle.ArticleStatus.UNPUBLISHED)
        self.assertIsNotNone(article.last_moderation_at)
        self.assertEqual(
            snapshot.moderation_status,
            ArticleSnapshot.SnapshotStatus.PENDING,
        )
        self.assertEqual(event.event_type, ArticleEvent.EventType.UNPUBLISH)

    def test_soft_delete_marks_source_article_deleted_and_removes_published_article(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PUBLISHED,
        )
        snapshot = create_article_snapshot(article)
        create_published_article(article, title=snapshot.title, content=snapshot.content)

        result = soft_delete(source_article_id=article.id, actor=self.author)

        article.refresh_from_db()
        event = ArticleEvent.objects.get(source_article=article)

        self.assertTrue(article.is_deleted)
        self.assertFalse(PublishedArticle.objects.filter(source_article=article).exists())
        self.assertEqual(event.event_type, ArticleEvent.EventType.DELETE)
        self.assertEqual(result["article_snapshot_id"], snapshot.id)

    def test_soft_delete_rejects_pending_article(self):
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PENDING,
        )

        with self.assertRaises(ServiceError) as exc:
            soft_delete(source_article_id=article.id, actor=self.author)

        self.assert_service_error(exc, code="state_transition_error")
        article.refresh_from_db()
        self.assertFalse(article.is_deleted)
