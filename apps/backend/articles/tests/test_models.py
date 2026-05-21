from django.db import IntegrityError, transaction

from articles.models import (
    ArticleEvent,
    ArticleSnapshot,
    Collection,
    CollectionItem,
    PublishedArticle,
    SourceArticle,
)
from articles.services.articles import ArticleWorkflow
from core.models import ContentTarget
from core.tests.factories import (
    create_collection,
    create_collection_item,
    create_published_article,
    create_source_article,
    create_user,
)
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

    def test_source_article_soft_delete_removes_published_article_and_collection_items(self):
        collection = create_collection(author=self.author)
        article = create_source_article(
            author=self.author,
            status=SourceArticle.ArticleStatus.PUBLISHED,
        )
        published = create_published_article(article)
        create_collection_item(collection, published)

        article.is_deleted = True
        article.save(update_fields=["is_deleted"])

        self.assertFalse(PublishedArticle.objects.filter(id=published.id).exists())
        self.assertFalse(CollectionItem.objects.filter(collection=collection).exists())

    def test_published_article_string_representation_references_source_article(self):
        article = create_source_article(author=self.author, title="Ship log")
        published = PublishedArticle.objects.create(
            source_article=article,
            title=article.title,
            html=article.markdown,
            publication_at=article.created_at,
        )

        self.assertEqual(str(published), "Published version of article Ship log")

    def test_published_article_created_directly_has_content_target(self):
        article = create_source_article(author=self.author, title="Targetable")

        published = PublishedArticle.objects.create(
            source_article=article,
            title=article.title,
            html=article.markdown,
            publication_at=article.created_at,
        )

        self.assertEqual(published.content_target.target_type, ContentTarget.TargetType.PUBLISHED_ARTICLE)
        self.assertEqual(published.content_target.published_article, published)

    def test_article_snapshot_string_representation_uses_source_article_id(self):
        article = create_source_article(author=self.author)
        snapshot = ArticleSnapshot.objects.create(
            source_article=article,
            title=article.title,
            markdown=article.markdown,
            hash="hash-value",
            source_version=article.version,
        )

        self.assertEqual(str(snapshot), f"Snapshot of article {article.id}")

    def test_article_event_string_representation_includes_operation_actor_and_article(self):
        article = create_source_article(author=self.author)
        snapshot = ArticleSnapshot.objects.create(
            source_article=article,
            title=article.title,
            markdown=article.markdown,
            hash=ArticleWorkflow._hash_and_normalize(article.title, article.markdown),
            source_version=article.version,
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

    def test_collection_string_representation_is_title(self):
        collection = create_collection(author=self.author, title="Redstone basics")

        self.assertEqual(str(collection), "Redstone basics")

    def test_collection_item_string_representation_references_article_and_collection(self):
        collection = create_collection(author=self.author, title="Playlist")
        article = create_source_article(author=self.author, title="Episode 1")
        published = create_published_article(article, title=article.title)
        item = create_collection_item(collection, published)

        self.assertEqual(str(item), "Published version of article Episode 1 in Playlist")

    def test_collection_item_rejects_duplicate_article_in_collection(self):
        collection = create_collection(author=self.author)
        article = create_source_article(author=self.author)
        published = create_published_article(article)
        create_collection_item(collection, published)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CollectionItem.objects.create(
                    collection=collection,
                    published_article=published,
                    position=2,
                )

    def test_collection_delete_removes_collection_items(self):
        collection = create_collection(author=self.author)
        article = create_source_article(author=self.author)
        published = create_published_article(article)
        create_collection_item(collection, published)
        collection_id = collection.id

        collection.delete()

        self.assertFalse(Collection.objects.filter(id=collection_id).exists())
        self.assertFalse(CollectionItem.objects.filter(collection_id=collection_id).exists())
