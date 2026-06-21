from django.urls import reverse

from rest_framework import status

from comments.models import Comment
from core.tests.factories import (
    create_comment,
    create_community_post,
    create_article_publication,
    create_article,
    create_user,
)
from core.tests.testcases import BaseAPITestCase


class CommentViewTests(BaseAPITestCase):
    def setUp(self):
        self.author = create_user(username="commenter")
        self.other_user = create_user(username="other-commenter")
        self.article = create_article(title="Guide")
        self.published = create_article_publication(self.article, title=self.article.source.title)

    def test_user_can_comment_on_article_publication(self):
        self.authenticate(self.author)
        response = self.post_json(
            reverse("comment-list"),
            {
                "article_publication": str(self.published.id),
                "body": "This is useful",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["author"], self.author.id)
        self.assert_uuid_equal(response.data["data"]["article_publication"], self.published.id)
        self.assertIsNone(response.data["data"]["parent"])
        self.assertEqual(response.data["data"]["body"], "This is useful")
        self.assertEqual(Comment.objects.count(), 1)

    def test_user_can_comment_on_community_post(self):
        post = create_community_post(author=self.author, body="Post")

        self.authenticate(self.other_user)
        response = self.post_json(
            reverse("comment-list"),
            {
                "community_post": str(post.id),
                "body": "A post comment",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["target"], post.content_target.id)
        self.assert_uuid_equal(response.data["data"]["community_post"], post.id)
        self.assertIsNone(response.data["data"]["article_publication"])
        self.assertEqual(Comment.objects.count(), 1)

    def test_user_can_reply_to_top_level_comment(self):
        parent = create_comment(self.author, self.published, body="Top level")

        self.authenticate(self.other_user)
        response = self.post_json(
            reverse("comment-list"),
            {
                "target": str(parent.content_target.id),
                "body": "A reply",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["parent"], parent.id)
        self.assert_uuid_equal(response.data["data"]["target"], parent.content_target.id)
        self.assert_uuid_equal(response.data["data"]["article_publication"], self.published.id)
        self.assertEqual(Comment.objects.count(), 2)

    def test_reply_to_reply_is_flattened_under_top_level_parent(self):
        parent = create_comment(self.author, self.published, body="Top level")
        reply = create_comment(self.other_user, self.published, reply_to=parent, body="Reply")

        self.authenticate(self.author)
        response = self.post_json(
            reverse("comment-list"),
            {
                "target": str(reply.content_target.id),
                "body": "Replying to a reply",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["parent"], parent.id)
        self.assert_uuid_equal(response.data["data"]["target"], reply.content_target.id)
        self.assertEqual(Comment.objects.count(), 3)

    def test_comment_mentions_render_with_current_usernames(self):
        self.authenticate(self.author)
        response = self.post_json(
            reverse("comment-list"),
            {
                "article_publication": str(self.published.id),
                "body": "{{mention:0}} and {{mention:1}}",
                "mentions": [str(self.other_user.id), str(self.author.id)],
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assertEqual(
            response.data["data"]["render_body"],
            "[@other-commenter](http://testserver/users/other-commenter) "
            "and [@commenter](http://testserver/users/commenter)",
        )
        self.assertEqual(
            response.data["data"]["mention_users"],
            [
                {
                    "user_id": str(self.other_user.id),
                    "username": "other-commenter",
                },
                {
                    "user_id": str(self.author.id),
                    "username": "commenter",
                },
            ],
        )

    def test_comment_rejects_unused_mentions(self):
        self.authenticate(self.author)
        response = self.post_json(
            reverse("comment-list"),
            {
                "article_publication": str(self.published.id),
                "body": "{{mention:0}}",
                "mentions": [str(self.other_user.id), str(self.author.id)],
            },
        )

        self.assert_error_response(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def test_author_can_edit_own_comment(self):
        comment = create_comment(self.author, self.published, body="Before")

        self.authenticate(self.author)
        response = self.patch_json(
            reverse("comment-detail", args=[comment.id]),
            {
                "body": "After",
            },
        )

        comment.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="updated",
        )
        self.assertEqual(comment.body, "After")

    def test_other_user_cannot_edit_comment(self):
        comment = create_comment(self.author, self.published, body="Before")

        self.authenticate(self.other_user)
        response = self.patch_json(
            reverse("comment-detail", args=[comment.id]),
            {
                "body": "After",
            },
        )

        comment.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(comment.body, "Before")

    def test_author_can_soft_delete_own_comment(self):
        comment = create_comment(self.author, self.published)

        self.authenticate(self.author)
        response = self.delete_json(reverse("comment-detail", args=[comment.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="deleted",
        )
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())
        self.assertTrue(Comment.all_objects.filter(id=comment.id, is_deleted=True).exists())

    def test_other_user_cannot_delete_comment(self):
        comment = create_comment(self.author, self.published)

        self.authenticate(self.other_user)
        response = self.delete_json(reverse("comment-detail", args=[comment.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())

    def test_list_filters_comments_by_article_publication(self):
        top_level = create_comment(self.author, self.published, body="Top level")
        reply = create_comment(self.other_user, self.published, reply_to=top_level, body="Reply")
        other_article = create_article(title="Other")
        other_published = create_article_publication(other_article, title=other_article.source.title)
        create_comment(self.author, other_published, body="Other")

        self.authenticate(self.author)
        response = self.get_json(
            reverse("comment-list"),
            {
                "article_publication": str(self.published.id),
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        comment_ids = {item["id"] for item in response.data["data"]["results"]}
        self.assertEqual(comment_ids, {str(top_level.id), str(reply.id)})

    def test_list_filters_comments_by_community_post(self):
        post = create_community_post(author=self.author, body="Post")
        other_post = create_community_post(author=self.author, body="Other")
        top_level = Comment.objects.create(
            author=self.author,
            target=post.content_target,
            body="Top level",
        )
        reply = create_comment(self.other_user, None, reply_to=top_level, body="Reply")
        Comment.objects.create(
            author=self.author,
            target=other_post.content_target,
            body="Other",
        )

        self.authenticate(self.author)
        response = self.get_json(
            reverse("comment-list"),
            {
                "community_post": str(post.id),
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        comment_ids = {item["id"] for item in response.data["data"]["results"]}
        self.assertEqual(comment_ids, {str(top_level.id), str(reply.id)})

    def test_article_publication_response_includes_comment_count(self):
        top_level = create_comment(self.author, self.published, body="Top level")
        create_comment(self.other_user, self.published, reply_to=top_level, body="Reply")
        deleted = create_comment(self.author, self.published, body="Deleted")
        deleted.is_deleted = True
        deleted.save(update_fields=["is_deleted"])

        self.authenticate(self.author)
        response = self.get_json(reverse("article_publication-detail", args=[self.published.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="retrieved",
        )
        self.assertEqual(response.data["data"]["comment_count"], 2)
