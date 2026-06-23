from django.db import transaction

from articles.models import ArticlePublication
from drf_std_response import ServiceError
from core.models import ContentTarget
from core.services.content_targets import (
    get_or_create_comment_target,
    get_or_create_community_post_target,
    get_or_create_article_publication_target,
)
from notifications.services import notify_comment_reply, notify_mentions
from posts.models import CommunityPost

from .models import Comment


@transaction.atomic
def create_comment(
    *,
    author,
    body: str,
    mentions: list,
    article_publication: ArticlePublication = None,
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
        if article_publication is None and community_post is None:
            raise ServiceError(
                detail="An article publication or community post is required",
                code="content_target_required",
            )
        parent = None
        if article_publication is not None:
            target = get_or_create_article_publication_target(article_publication)
        else:
            target = get_or_create_community_post_target(community_post)

    comment = Comment.objects.create(
        author=author,
        target=target,
        parent=parent,
        body=body,
        mentions=mentions,
    )
    comment_target = get_or_create_comment_target(comment)
    notify_mentions(
        actor=author,
        target=comment_target,
        mention_user_ids=mentions,
        dedupe_prefix=f"comment:{comment.id}:created",
    )
    if target.comment_id is not None:
        notify_comment_reply(comment=comment)
    return comment


def update_comment(*, comment: Comment, body: str, mentions: list):
    previous_mentions = set(comment.mentions)
    comment.body = body
    comment.mentions = mentions
    comment.save(update_fields=["body", "mentions", "updated_at"])
    notify_mentions(
        actor=comment.author,
        target=comment.content_target,
        mention_user_ids=set(mentions) - previous_mentions,
        dedupe_prefix=f"comment:{comment.id}:updated",
    )
    return comment


def soft_delete_comment(comment: Comment):
    comment.is_deleted = True
    comment.save(update_fields=["is_deleted", "updated_at"])
    return comment


def get_article_publication_target(article_publication_id):
    try:
        return ContentTarget.objects.get(
            target_type=ContentTarget.TargetType.ARTICLE_PUBLICATION,
            article_publication_id=article_publication_id,
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
