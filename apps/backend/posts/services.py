from .models import CommunityPost


def create_community_post(*, author, body: str):
    return CommunityPost.objects.create(author=author, body=body)


def update_community_post(*, post: CommunityPost, body: str):
    post.body = body
    post.save(update_fields=["body", "updated_at"])
    return post


def soft_delete_community_post(post: CommunityPost):
    post.is_deleted = True
    post.save(update_fields=["is_deleted", "updated_at"])
    return post
