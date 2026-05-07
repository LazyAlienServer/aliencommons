from django.contrib.auth import get_user_model
from django.utils import timezone

from articles.models import ArticleSnapshot, Collection, CollectionItem, PublishedArticle, SourceArticle
from articles.services.articles import ArticleWorkflow

from .helpers import unique_suffix


User = get_user_model()


def create_user(**kwargs):
    suffix = unique_suffix()
    defaults = {
        "username": f"user-{suffix}",
        "password": "secret123",
    }
    defaults.update(kwargs)
    password = defaults.pop("password")

    return User.objects.create_user(password=password, **defaults)


def create_moderator(**kwargs):
    kwargs.setdefault("is_moderator", True)
    return create_user(**kwargs)


def create_source_article(**kwargs):
    defaults = {
        "author": kwargs.pop("author", create_user()),
        "title": "First draft",
        "markdown": "Hello",
        "status": SourceArticle.ArticleStatus.DRAFT,
    }
    defaults.update(kwargs)
    return SourceArticle.objects.create(**defaults)


def create_article_snapshot(article, **kwargs):
    defaults = {
        "source_article": article,
        "title": article.title,
        "markdown": article.markdown,
        "hash": ArticleWorkflow._hash_and_normalize(
            article.title,
            article.markdown,
        ),
        "source_version": article.version,
        "moderation_status": ArticleSnapshot.SnapshotStatus.PENDING,
    }
    defaults.update(kwargs)
    return ArticleSnapshot.objects.create(**defaults)


def create_published_article(article, **kwargs):
    defaults = {
        "source_article": article,
        "title": article.title,
        "html": article.markdown,
        "publication_at": timezone.now(),
    }
    defaults.update(kwargs)
    return PublishedArticle.objects.create(**defaults)


def create_collection(**kwargs):
    defaults = {
        "author": kwargs.pop("author", create_user()),
        "title": "Collection",
        "description": "",
    }
    defaults.update(kwargs)
    return Collection.objects.create(**defaults)


def create_collection_item(collection, published_article, **kwargs):
    defaults = {
        "collection": collection,
        "published_article": published_article,
        "position": 1,
    }
    defaults.update(kwargs)
    return CollectionItem.objects.create(**defaults)
