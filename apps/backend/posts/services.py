from core.services.content_targets import get_or_create_community_post_target

from .models import CommunityPost


def create_community_post(*, author, body: str, mentions: list = None):
    post = CommunityPost.objects.create(author=author, body=body, mentions=mentions or [])
    get_or_create_community_post_target(post)
    return post


def update_community_post(*, post: CommunityPost, body: str, mentions: list = None):
    post.body = body
    if mentions is not None:
        post.mentions = mentions
    post.save(update_fields=["body", "mentions", "updated_at"])
    return post


def soft_delete_community_post(post: CommunityPost):
    post.is_deleted = True
    post.save(update_fields=["is_deleted", "updated_at"])
    return post
