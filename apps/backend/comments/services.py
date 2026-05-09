from django.db import transaction

from articles.models import PublishedArticle
from core.exceptions import ServiceError
from core.models import ContentTarget
from core.services.content_targets import (
    get_or_create_comment_target,
    get_or_create_published_article_target,
)

from .models import Comment


@transaction.atomic
def create_comment(*, author, body: str, published_article: PublishedArticle = None, parent: Comment = None):
    if parent is not None:
        if parent.parent_id is not None:
            raise ServiceError(
                detail="Replies cannot have replies",
                code="nested_comment_not_allowed",
            )
        target = get_or_create_comment_target(parent)
    else:
        if published_article is None:
            raise ServiceError(
                detail="A published article is required",
                code="published_article_required",
            )
        target = get_or_create_published_article_target(published_article)

    comment = Comment.objects.create(
        author=author,
        target=target,
        parent=parent,
        body=body,
    )
    get_or_create_comment_target(comment)
    return comment


def update_comment(*, comment: Comment, body: str):
    comment.body = body
    comment.save(update_fields=["body", "updated_at"])
    return comment


def soft_delete_comment(comment: Comment):
    comment.is_deleted = True
    comment.save(update_fields=["is_deleted", "updated_at"])
    return comment


def get_published_article_target(published_article_id):
    try:
        return ContentTarget.objects.get(
            target_type=ContentTarget.TargetType.PUBLISHED_ARTICLE,
            published_article_id=published_article_id,
        )
    except ContentTarget.DoesNotExist:
        return None

