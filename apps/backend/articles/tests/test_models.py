from django.db import IntegrityError, transaction

from articles.models import (
    ArticleEvent,
    ArticleSnapshot,
    Collection,
    CollectionItem,
    ArticlePublication,
    ArticlePublicationVersion,
    Article,
)
from articles.services.articles import ArticleWorkflow
from core.models import ContentTarget
from core.tests.factories import (
    create_collection,
    create_collection_item,
    create_article_publication,
    create_article,
    create_user,
)
from core.tests.testcases import BaseTestCase


class ArticleModelTests(BaseTestCase):
    def setUp(self):
        self.author = create_user(username="author")

    def test_article_string_representation_is_title(self):
        article = create_article(author=self.author, title="Readable title")

        self.assertEqual(str(article), "Readable title")

    def test_article_default_manager_excludes_soft_deleted_rows(self):
        article = create_article(author=self.author)
        article.is_deleted = True
        article.save(update_fields=["is_deleted"])

        self.assertFalse(Article.objects.filter(id=article.id).exists())
        self.assertTrue(Article.all_objects.filter(id=article.id).exists())

    def test_article_soft_delete_removes_article_publication_and_collection_items(self):
        collection = create_collection(author=self.author)
        article = create_article(
            author=self.author,
            status=Article.ArticleStatus.PUBLISHED,
        )
        published = create_article_publication(article)
        create_collection_item(collection, published)

        article.is_deleted = True
        article.save(update_fields=["is_deleted"])

        self.assertFalse(ArticlePublication.objects.filter(id=published.id).exists())
        self.assertFalse(CollectionItem.objects.filter(collection=collection).exists())

    def test_article_publication_string_representation_references_article(self):
        article = create_article(author=self.author, title="Ship log")
        published = create_article_publication(article)

        self.assertEqual(str(published), "Publication of article Ship log")

    def test_article_publication_created_directly_has_content_target(self):
        article = create_article(author=self.author, title="Targetable")

        published = create_article_publication(article)

        self.assertEqual(published.content_target.target_type, ContentTarget.TargetType.ARTICLE_PUBLICATION)
        self.assertEqual(published.content_target.article_publication, published)

    def test_article_publication_version_string_representation_references_version(self):
        article = create_article(author=self.author, title="Ship log")
        published = create_article_publication(article)
        published_version = ArticlePublicationVersion.objects.get(publication=published)

        self.assertEqual(str(published_version), "Publication of article Ship log v1")

    def test_article_publication_latest_version_returns_highest_version(self):
        article = create_article(author=self.author, title="Ship log")
        published = create_article_publication(article, version=1, title="First")
        create_article_publication(article, version=2, title="Second")

        self.assertEqual(published.latest_version().version, 2)
        self.assertEqual(published.latest_version().title, "Second")

    def test_article_snapshot_string_representation_uses_article_id(self):
        article = create_article(author=self.author)
        snapshot = ArticleSnapshot.objects.create(
            article=article,
            title=article.source.title,
            markdown=article.source.markdown,
            hash="hash-value",
            source_version=article.source.version,
        )

        self.assertEqual(str(snapshot), f"Snapshot of article {article.id}")

    def test_article_event_string_representation_includes_operation_actor_and_article(self):
        article = create_article(author=self.author)
        snapshot = ArticleSnapshot.objects.create(
            article=article,
            title=article.source.title,
            markdown=article.source.markdown,
            hash=ArticleWorkflow._hash_and_normalize(article.source.title, article.source.markdown),
            source_version=article.source.version,
        )
        event = ArticleEvent.objects.create(
            article=article,
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
        article = create_article(author=self.author, title="Episode 1")
        published = create_article_publication(article, title=article.source.title)
        item = create_collection_item(collection, published)

        self.assertEqual(str(item), "Publication of article Episode 1 in Playlist")

    def test_collection_item_rejects_duplicate_article_in_collection(self):
        collection = create_collection(author=self.author)
        article = create_article(author=self.author)
        published = create_article_publication(article)
        create_collection_item(collection, published)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CollectionItem.objects.create(
                    collection=collection,
                    article_publication=published,
                    position=2,
                )

    def test_collection_delete_removes_collection_items(self):
        collection = create_collection(author=self.author)
        article = create_article(author=self.author)
        published = create_article_publication(article)
        create_collection_item(collection, published)
        collection_id = collection.id

        collection.delete()

        self.assertFalse(Collection.objects.filter(id=collection_id).exists())
        self.assertFalse(CollectionItem.objects.filter(collection_id=collection_id).exists())
