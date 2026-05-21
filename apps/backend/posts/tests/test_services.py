from core.tests.factories import create_user
from core.tests.testcases import BaseTestCase
from posts.models import CommunityPost
from posts.services import (
    create_community_post,
    soft_delete_community_post,
    update_community_post,
)


class CommunityPostServiceTests(BaseTestCase):
    def test_create_community_post_returns_created_post(self):
        author = create_user(username="post-author")

        post = create_community_post(author=author, body="Hello community")

        self.assertEqual(post.author, author)
        self.assertEqual(post.body, "Hello community")
        self.assertTrue(CommunityPost.objects.filter(id=post.id).exists())
        self.assertEqual(post.content_target.community_post, post)

    def test_update_community_post_updates_body_and_returns_post(self):
        author = create_user(username="post-author")
        post = CommunityPost.objects.create(author=author, body="Before")

        updated = update_community_post(post=post, body="After")

        post.refresh_from_db()
        self.assertEqual(updated, post)
        self.assertEqual(post.body, "After")

    def test_update_community_post_updates_mentions(self):
        author = create_user(username="post-author")
        mentioned = create_user(username="mentioned")
        post = CommunityPost.objects.create(author=author, body="Before")

        update_community_post(
            post=post,
            body="{{mention:0}}",
            mentions=[str(mentioned.id)],
        )

        post.refresh_from_db()
        self.assertEqual(post.mentions, [str(mentioned.id)])

    def test_soft_delete_community_post_marks_post_deleted_and_returns_post(self):
        author = create_user(username="post-author")
        post = CommunityPost.objects.create(author=author, body="Hello community")

        deleted = soft_delete_community_post(post)

        post.refresh_from_db()
        self.assertEqual(deleted, post)
        self.assertTrue(post.is_deleted)
