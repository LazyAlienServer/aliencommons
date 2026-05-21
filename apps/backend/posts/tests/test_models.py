from core.models import ContentTarget
from core.tests.factories import create_community_post, create_user
from core.tests.testcases import BaseTestCase
from posts.models import CommunityPost


class CommunityPostModelTests(BaseTestCase):
    def test_post_creation_with_author(self):
        author = create_user(username="post-author")

        post = create_community_post(author=author, body="Hello community")

        self.assertEqual(post.author, author)
        self.assertEqual(post.body, "Hello community")
        self.assertFalse(post.is_deleted)
        self.assertTrue(CommunityPost.objects.filter(id=post.id).exists())
        self.assertEqual(post.content_target.target_type, ContentTarget.TargetType.COMMUNITY_POST)
        self.assertEqual(post.content_target.community_post, post)

    def test_post_created_directly_has_content_target(self):
        author = create_user(username="direct-post-author")

        post = CommunityPost.objects.create(author=author, body="Direct")

        self.assertEqual(post.content_target.target_type, ContentTarget.TargetType.COMMUNITY_POST)
        self.assertEqual(post.content_target.community_post, post)

    def test_posts_are_ordered_newest_first(self):
        author = create_user(username="post-author")
        older = create_community_post(author=author, body="Older")
        newer = create_community_post(author=author, body="Newer")

        posts = list(CommunityPost.objects.all())

        self.assertEqual(posts, [newer, older])

    def test_soft_deleted_posts_are_excluded_from_default_manager(self):
        post = create_community_post(body="Deleted")

        post.is_deleted = True
        post.save(update_fields=["is_deleted"])

        self.assertFalse(CommunityPost.objects.filter(id=post.id).exists())
        self.assertTrue(CommunityPost.all_objects.filter(id=post.id, is_deleted=True).exists())

    def test_string_representation_includes_post_and_author_ids(self):
        author = create_user(username="post-author")
        post = create_community_post(author=author, body="Hello community")

        self.assertEqual(str(post), f"Post {post.id} by {author.id}")

    def test_post_delete_cascades_content_target(self):
        post = create_community_post()
        target_id = post.content_target.id

        post.delete()

        self.assertFalse(ContentTarget.objects.filter(id=target_id).exists())
