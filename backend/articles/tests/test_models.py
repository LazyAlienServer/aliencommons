from articles.models import (
    ArticleEvent,
    ArticleSnapshot,
    PublishedArticle,
    SourceArticle,
)
from core.tests.factories import create_source_article, create_user
from core.tests.testcases import BaseTestCase


class ArticleModelTests(BaseTestCase):
    def setUp(self):
        self.author = create_user(username="author")

    def test_source_article_string_representation_is_title(self):
        article = create_source_article(author=self.author, title="Readable title")

        self.assertEqual(str(article), "Readable title")

    def test_source_article_default_manager_excludes_soft_deleted_rows(self):
        article = create_source_article(author=self.author)
        article.is_deleted = True
        article.save(update_fields=["is_deleted"])

        self.assertFalse(SourceArticle.objects.filter(id=article.id).exists())
        self.assertTrue(SourceArticle.all_objects.filter(id=article.id).exists())

    def test_published_article_string_representation_references_source_article(self):
        article = create_source_article(author=self.author, title="Ship log")
        published = PublishedArticle.objects.create(
            source_article=article,
            title=article.title,
            content=article.content,
        )

        self.assertEqual(str(published), "Published version of article Ship log")

    def test_article_snapshot_string_representation_uses_source_article_id(self):
        article = create_source_article(author=self.author)
        snapshot = ArticleSnapshot.objects.create(
            source_article=article,
            title=article.title,
            content=article.content,
            content_hash="hash-value",
        )

        self.assertEqual(str(snapshot), f"Snapshot of article {article.id}")

    def test_article_event_string_representation_includes_operation_actor_and_article(self):
        article = create_source_article(author=self.author)
        snapshot = ArticleSnapshot.objects.create(
            source_article=article,
            title=article.title,
            content=article.content,
            content_hash="hash-value",
        )
        event = ArticleEvent.objects.create(
            source_article=article,
            article_snapshot=snapshot,
            event_type=ArticleEvent.EventType.APPROVE,
            actor=self.author,
        )

        self.assertEqual(
            str(event),
            f"Operation Approve by {self.author.id} on article {article.id}",
        )
