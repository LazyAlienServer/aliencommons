from core.services.content_targets import get_or_create_community_post_target
from notifications.services import notify_mentions, notify_subscribed_author_posted

from .models import CommunityPost


def create_community_post(*, author, body: str, mentions: list = None):
    post = CommunityPost.objects.create(author=author, body=body, mentions=mentions or [])
    target = get_or_create_community_post_target(post)
    notify_mentions(
        actor=author,
        target=target,
        mention_user_ids=post.mentions,
        dedupe_prefix=f"community-post:{post.id}:created",
    )
    notify_subscribed_author_posted(
        actor=author,
        target=target,
        content_kind="community_post",
    )
    return post


def update_community_post(*, post: CommunityPost, body: str, mentions: list = None):
    previous_mentions = set(post.mentions)
    post.body = body
    if mentions is not None:
        post.mentions = mentions
    post.save(update_fields=["body", "mentions", "updated_at"])
    notify_mentions(
        actor=post.author,
        target=post.content_target,
        mention_user_ids=set(post.mentions) - previous_mentions,
        dedupe_prefix=f"community-post:{post.id}:updated",
    )
    return post


def soft_delete_community_post(post: CommunityPost):
    post.is_deleted = True
    post.save(update_fields=["is_deleted", "updated_at"])
    return post
