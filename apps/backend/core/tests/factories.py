from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

from articles.models import ArticleSnapshot, Collection, CollectionItem, PublishedArticle, SourceArticle
from articles.services.articles import ArticleWorkflow
from bookmarks.models import Bookmark, BookmarkFolder
from comments.models import Comment
from core.models import ContentTarget
from core.services.content_targets import (
    get_or_create_comment_target,
    get_or_create_published_article_target,
)
from reactions.models import Reaction
from reports.models import ContentReport, UserReport
from posts.services import create_community_post as create_community_post_service

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

    user = User.objects.create_user(password=password, **defaults)
    BookmarkFolder.objects.create(user=user, name=settings.DEFAULT_BOOKMARK_FOLDER_NAME)
    return user


def create_moderator(**kwargs):
    kwargs.setdefault("is_moderator", True)
    return create_user(**kwargs)


def create_source_article(**kwargs):
    defaults = {
        "author": kwargs.pop("author", create_user()),
        "title": "First draft",
        "markdown": "# First draft\n\nHello",
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


def create_bookmark_folder(**kwargs):
    defaults = {
        "user": kwargs.pop("user", create_user()),
        "name": f"Folder {unique_suffix()}",
    }
    defaults.update(kwargs)
    return BookmarkFolder.objects.create(**defaults)


def create_bookmark(user, published_article, folder=None, **kwargs):
    defaults = {
        "user": user,
        "folder": folder or create_bookmark_folder(user=user),
        "published_article": published_article,
    }
    defaults.update(kwargs)
    return Bookmark.objects.create(**defaults)


def create_content_target(published_article, **kwargs):
    if not kwargs:
        return get_or_create_published_article_target(published_article)

    defaults = {
        "target_type": ContentTarget.TargetType.PUBLISHED_ARTICLE,
        "published_article": published_article,
    }
    defaults.update(kwargs)
    return ContentTarget.objects.create(**defaults)


def create_reaction(user, published_article, **kwargs):
    target = kwargs.pop("target", None) or get_or_create_published_article_target(published_article)
    defaults = {
        "user": user,
        "target": target,
        "reaction_type": Reaction.ReactionType.LIKE,
    }
    defaults.update(kwargs)
    return Reaction.objects.create(**defaults)


def create_comment(author, published_article, **kwargs):
    reply_to = kwargs.pop("reply_to", None)
    if reply_to is not None:
        target = kwargs.pop("target", get_or_create_comment_target(reply_to))
        parent = kwargs.pop("parent", reply_to if reply_to.parent_id is None else reply_to.parent)
    else:
        parent = kwargs.pop("parent", None)
        target = kwargs.pop(
            "target",
            get_or_create_comment_target(parent) if parent else get_or_create_published_article_target(published_article),
        )
    body = kwargs.pop("body", "A thoughtful comment")
    mentions = kwargs.pop("mentions", [])
    comment = Comment.objects.create(
        author=author,
        target=target,
        parent=parent,
        body=body,
        mentions=mentions,
        **kwargs,
    )
    get_or_create_comment_target(comment)
    return comment


def create_community_post(author=None, body="Test post", **kwargs):
    if author is None:
        author = create_user()

    defaults = {
        "author": author,
        "body": body,
    }
    defaults.update(kwargs)
    return create_community_post_service(**defaults)


def create_content_report(reporter, target, **kwargs):
    from reports.services import build_content_report_snapshot

    snapshot = kwargs.pop("snapshot", build_content_report_snapshot(target))
    defaults = {
        "reporter": reporter,
        "target": target,
        "target_type": target.target_type,
        "target_object_id": snapshot["target_object_id"],
        "reason": ContentReport.ReportReason.SPAM,
        "description": "",
        "snapshot": snapshot,
    }
    defaults.update(kwargs)
    return ContentReport.objects.create(**defaults)


def create_user_report(reporter, reported_user, **kwargs):
    from reports.services import build_user_report_snapshot

    snapshot = kwargs.pop("snapshot", build_user_report_snapshot(reported_user))
    defaults = {
        "reporter": reporter,
        "reported_user": reported_user,
        "reported_user_id_snapshot": reported_user.id,
        "reason": UserReport.ReportReason.SPAM,
        "description": "",
        "snapshot": snapshot,
    }
    defaults.update(kwargs)
    return UserReport.objects.create(**defaults)
