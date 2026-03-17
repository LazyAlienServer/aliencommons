from django.contrib.auth import get_user_model

from articles.models import ArticleSnapshot, PublishedArticle, SourceArticle
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
        "content": {"blocks": [{"type": "paragraph", "text": "Hello"}]},
        "status": SourceArticle.ArticleStatus.DRAFT,
    }
    defaults.update(kwargs)
    return SourceArticle.objects.create(**defaults)


def create_article_snapshot(article, **kwargs):
    defaults = {
        "source_article": article,
        "title": article.title,
        "content": article.content,
        "content_hash": ArticleWorkflow._hash_and_normalize(
            article.title,
            article.content,
        ),
        "moderation_status": ArticleSnapshot.SnapshotStatus.PENDING,
    }
    defaults.update(kwargs)
    return ArticleSnapshot.objects.create(**defaults)


def create_published_article(article, **kwargs):
    defaults = {
        "source_article": article,
        "title": article.title,
        "content": article.content,
    }
    defaults.update(kwargs)
    return PublishedArticle.objects.create(**defaults)
