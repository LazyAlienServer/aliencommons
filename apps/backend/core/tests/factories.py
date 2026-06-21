from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Max
from django.utils import timezone

from articles.models import (
    Article,
    ArticlePublication,
    ArticlePublicationVersion,
    ArticleSnapshot,
    ArticleSource,
    Collection,
    CollectionItem,
)
from articles.services.articles import ArticleWorkflow
from bookmarks.models import Bookmark, BookmarkFolder
from comments.models import Comment
from core.models import ContentTarget
from core.services.content_targets import (
    get_or_create_comment_target,
    get_or_create_article_publication_target,
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


def create_article(**kwargs):
    title = kwargs.pop("title", "First draft")
    markdown = kwargs.pop("markdown", "# First draft\n\nHello")
    version = kwargs.pop("version", 1)
    defaults = {
        "author": kwargs.pop("author", create_user()),
        "status": Article.ArticleStatus.DRAFT,
    }
    defaults.update(kwargs)
    article = Article.objects.create(**defaults)
    ArticleSource.objects.create(
        article=article,
        title=title,
        markdown=markdown,
        version=version,
    )
    return article


def create_article_snapshot(article, **kwargs):
    defaults = {
        "article": article,
        "title": article.source.title,
        "markdown": article.source.markdown,
        "hash": ArticleWorkflow._hash_and_normalize(
            article.source.title,
            article.source.markdown,
        ),
        "source_version": article.source.version,
        "moderation_status": ArticleSnapshot.SnapshotStatus.PENDING,
    }
    defaults.update(kwargs)
    return ArticleSnapshot.objects.create(**defaults)


def create_article_publication(article, **kwargs):
    approved_snapshot = kwargs.pop("approved_snapshot", None)
    publication_at = kwargs.pop("publication_at", timezone.now())
    version = kwargs.pop("version", None)
    title = kwargs.pop("title", article.source.title)
    html = kwargs.pop("html", article.source.markdown)
    if approved_snapshot is None:
        approved_snapshot = (
            article.article_snapshots
            .filter(publication_version__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if approved_snapshot is None:
            approved_snapshot = create_article_snapshot(article)
        if approved_snapshot.moderation_status != ArticleSnapshot.SnapshotStatus.APPROVED:
            approved_snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.APPROVED
            approved_snapshot.save(update_fields=["moderation_status"])
    if article.status == Article.ArticleStatus.DRAFT:
        article.status = Article.ArticleStatus.PUBLISHED
        article.save(update_fields=["status"])

    publication, _ = ArticlePublication.objects.get_or_create(
        article=article,
        defaults={"published_at": publication_at},
    )
    if version is None:
        version = (publication.versions.aggregate(max_version=Max("version"))["max_version"] or 0) + 1

    version_defaults = {
        "publication": publication,
        "approved_snapshot": approved_snapshot,
        "version": version,
        "title": title,
        "html": html,
        "publication_at": publication_at,
    }
    version_defaults.update(kwargs)
    ArticlePublicationVersion.objects.create(**version_defaults)
    return publication


def create_collection(**kwargs):
    defaults = {
        "author": kwargs.pop("author", create_user()),
        "title": "Collection",
        "description": "",
    }
    defaults.update(kwargs)
    return Collection.objects.create(**defaults)


def create_collection_item(collection, article_publication, **kwargs):
    defaults = {
        "collection": collection,
        "article_publication": article_publication,
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


def create_bookmark(user, article_publication, folder=None, **kwargs):
    defaults = {
        "user": user,
        "folder": folder or create_bookmark_folder(user=user),
        "article_publication": article_publication,
    }
    defaults.update(kwargs)
    return Bookmark.objects.create(**defaults)


def create_content_target(article_publication, **kwargs):
    if not kwargs:
        return get_or_create_article_publication_target(article_publication)

    defaults = {
        "target_type": ContentTarget.TargetType.ARTICLE_PUBLICATION,
        "article_publication": article_publication,
    }
    defaults.update(kwargs)
    return ContentTarget.objects.create(**defaults)


def create_reaction(user, article_publication, **kwargs):
    target = kwargs.pop("target", None) or get_or_create_article_publication_target(article_publication)
    defaults = {
        "user": user,
        "target": target,
        "reaction_type": Reaction.ReactionType.LIKE,
    }
    defaults.update(kwargs)
    return Reaction.objects.create(**defaults)


def create_comment(author, article_publication, **kwargs):
    reply_to = kwargs.pop("reply_to", None)
    if reply_to is not None:
        target = kwargs.pop("target", get_or_create_comment_target(reply_to))
        parent = kwargs.pop("parent", reply_to if reply_to.parent_id is None else reply_to.parent)
    else:
        parent = kwargs.pop("parent", None)
        target = kwargs.pop(
            "target",
            get_or_create_comment_target(parent) if parent else get_or_create_article_publication_target(article_publication),
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
