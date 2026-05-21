from django.db import transaction

from articles.models import PublishedArticle
from core.exceptions import ServiceError
from core.models import ContentTarget
from core.services.content_targets import (
    get_or_create_comment_target,
    get_or_create_community_post_target,
    get_or_create_published_article_target,
)
from posts.models import CommunityPost

from .models import Comment


@transaction.atomic
def create_comment(
    *,
    author,
    body: str,
    mentions: list,
    published_article: PublishedArticle = None,
    community_post: CommunityPost = None,
    target=None,
):
    if target is not None:
        if target.comment_id is None:
            raise ServiceError(
                detail="Comment replies must target a comment",
                code="invalid_comment_reply_target",
            )
        target_comment = target.comment
        parent = target_comment if target_comment.parent_id is None else target_comment.parent
    else:
        if published_article is None and community_post is None:
            raise ServiceError(
                detail="A published article or community post is required",
                code="content_target_required",
            )
        parent = None
        if published_article is not None:
            target = get_or_create_published_article_target(published_article)
        else:
            target = get_or_create_community_post_target(community_post)

    comment = Comment.objects.create(
        author=author,
        target=target,
        parent=parent,
        body=body,
        mentions=mentions,
    )
    get_or_create_comment_target(comment)
    return comment


def update_comment(*, comment: Comment, body: str, mentions: list):
    comment.body = body
    comment.mentions = mentions
    comment.save(update_fields=["body", "mentions", "updated_at"])
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


def get_community_post_target(community_post_id):
    try:
        return ContentTarget.objects.get(
            target_type=ContentTarget.TargetType.COMMUNITY_POST,
            community_post_id=community_post_id,
        )
    except ContentTarget.DoesNotExist:
        return None
