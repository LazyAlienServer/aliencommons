from django.urls import reverse

from rest_framework import status

from comments.models import Comment
from core.tests.factories import (
    create_comment,
    create_published_article,
    create_source_article,
    create_user,
)
from core.tests.testcases import BaseAPITestCase


class CommentViewTests(BaseAPITestCase):
    def setUp(self):
        self.author = create_user(username="commenter")
        self.other_user = create_user(username="other-commenter")
        self.article = create_source_article(title="Guide")
        self.published = create_published_article(self.article, title=self.article.title)

    def test_user_can_comment_on_published_article(self):
        self.authenticate(self.author)
        response = self.post_json(
            reverse("comment-list"),
            {
                "published_article": str(self.published.id),
                "body": "This is useful",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["author"], self.author.id)
        self.assert_uuid_equal(response.data["data"]["published_article"], self.published.id)
        self.assertIsNone(response.data["data"]["parent"])
        self.assertEqual(response.data["data"]["body"], "This is useful")
        self.assertEqual(Comment.objects.count(), 1)

    def test_user_can_reply_to_top_level_comment(self):
        parent = create_comment(self.author, self.published, body="Top level")

        self.authenticate(self.other_user)
        response = self.post_json(
            reverse("comment-list"),
            {
                "parent": str(parent.id),
                "body": "A reply",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["parent"], parent.id)
        self.assert_uuid_equal(response.data["data"]["published_article"], self.published.id)
        self.assertEqual(Comment.objects.count(), 2)

    def test_user_cannot_reply_to_reply(self):
        parent = create_comment(self.author, self.published, body="Top level")
        reply = create_comment(self.other_user, self.published, parent=parent, body="Reply")

        self.authenticate(self.author)
        response = self.post_json(
            reverse("comment-list"),
            {
                "parent": str(reply.id),
                "body": "Nested reply",
            },
        )

        self.assert_error_response(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(Comment.objects.count(), 2)

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

    def test_list_filters_comments_by_published_article(self):
        top_level = create_comment(self.author, self.published, body="Top level")
        reply = create_comment(self.other_user, self.published, parent=top_level, body="Reply")
        other_article = create_source_article(title="Other")
        other_published = create_published_article(other_article, title=other_article.title)
        create_comment(self.author, other_published, body="Other")

        self.authenticate(self.author)
        response = self.get_json(
            reverse("comment-list"),
            {
                "published_article": str(self.published.id),
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        comment_ids = {item["id"] for item in response.data["data"]["results"]}
        self.assertEqual(comment_ids, {str(top_level.id), str(reply.id)})

    def test_published_article_response_includes_comment_count(self):
        top_level = create_comment(self.author, self.published, body="Top level")
        create_comment(self.other_user, self.published, parent=top_level, body="Reply")
        deleted = create_comment(self.author, self.published, body="Deleted")
        deleted.is_deleted = True
        deleted.save(update_fields=["is_deleted"])

        self.authenticate(self.author)
        response = self.get_json(reverse("published_article-detail", args=[self.published.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="retrieved",
        )
        self.assertEqual(response.data["data"]["comment_count"], 2)

