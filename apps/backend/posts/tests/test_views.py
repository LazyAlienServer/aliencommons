from django.urls import reverse

from rest_framework import status

from core.tests.factories import create_community_post, create_user
from core.tests.testcases import BaseAPITestCase
from posts.models import CommunityPost


class CommunityPostViewTests(BaseAPITestCase):
    def setUp(self):
        self.author = create_user(username="post-author")
        self.other_user = create_user(username="other-user")

    def test_list_returns_authenticated_visible_posts_newest_first(self):
        older = create_community_post(author=self.author, body="Older")
        deleted = create_community_post(author=self.author, body="Deleted")
        deleted.is_deleted = True
        deleted.save(update_fields=["is_deleted"])
        newer = create_community_post(author=self.other_user, body="Newer")

        self.authenticate(self.author)
        response = self.get_json(reverse("community_post-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        post_ids = [item["id"] for item in response.data["data"]["results"]]
        self.assertEqual(post_ids, [str(newer.id), str(older.id)])

    def test_authenticated_user_can_retrieve_post(self):
        post = create_community_post(author=self.author, body="Hello community")

        self.authenticate(self.other_user)
        response = self.get_json(reverse("community_post-detail", args=[post.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="retrieved",
        )
        self.assert_uuid_equal(response.data["data"]["id"], post.id)
        self.assertEqual(response.data["data"]["body"], "Hello community")
        self.assertEqual(response.data["data"]["author_username"], "post-author")

    def test_authenticated_user_can_create_post_as_request_user(self):
        self.authenticate(self.author)
        response = self.post_json(
            reverse("community_post-list"),
            {
                "body": "Hello community",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        post = CommunityPost.objects.get()
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.body, "Hello community")
        self.assert_uuid_equal(response.data["data"]["author"]["id"], self.author.id)

    def test_author_can_update_own_post(self):
        post = create_community_post(author=self.author, body="Before")

        self.authenticate(self.author)
        response = self.patch_json(
            reverse("community_post-detail", args=[post.id]),
            {
                "body": "After",
            },
        )

        post.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="updated",
        )
        self.assertEqual(post.body, "After")
        self.assertEqual(response.data["data"]["body"], "After")

    def test_author_can_patch_post_without_body(self):
        post = create_community_post(author=self.author, body="Before")

        self.authenticate(self.author)
        response = self.patch_json(
            reverse("community_post-detail", args=[post.id]),
            {},
        )

        post.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="updated",
        )
        self.assertEqual(post.body, "Before")
        self.assertEqual(response.data["data"]["body"], "Before")

    def test_other_user_cannot_update_post(self):
        post = create_community_post(author=self.author, body="Before")

        self.authenticate(self.other_user)
        response = self.patch_json(
            reverse("community_post-detail", args=[post.id]),
            {
                "body": "After",
            },
        )

        post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(post.body, "Before")

    def test_author_can_destroy_own_post_with_soft_delete(self):
        post = create_community_post(author=self.author, body="Hello community")

        self.authenticate(self.author)
        response = self.delete_json(reverse("community_post-detail", args=[post.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="deleted",
        )
        self.assertEqual(response.content, response.rendered_content)
        self.assertIn(b'"success":true', response.content)
        self.assertFalse(CommunityPost.objects.filter(id=post.id).exists())
        self.assertTrue(CommunityPost.all_objects.filter(id=post.id, is_deleted=True).exists())

    def test_authenticated_user_can_retrieve_post_without_author(self):
        post = CommunityPost.objects.create(author=None, body="Orphaned post")

        self.authenticate(self.other_user)
        response = self.get_json(reverse("community_post-detail", args=[post.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="retrieved",
        )
        self.assertIsNone(response.data["data"]["author"])
        self.assertIsNone(response.data["data"]["author_username"])

    def test_other_user_cannot_destroy_post(self):
        post = create_community_post(author=self.author, body="Hello community")

        self.authenticate(self.other_user)
        response = self.delete_json(reverse("community_post-detail", args=[post.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CommunityPost.objects.filter(id=post.id).exists())

    def test_anonymous_users_cannot_access_posts(self):
        post = create_community_post(author=self.author, body="Hello community")

        responses = [
            self.get_json(reverse("community_post-list")),
            self.get_json(reverse("community_post-detail", args=[post.id])),
            self.post_json(reverse("community_post-list"), {"body": "Hello"}),
            self.patch_json(reverse("community_post-detail", args=[post.id]), {"body": "After"}),
            self.delete_json(reverse("community_post-detail", args=[post.id])),
        ]

        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_rejects_invalid_body_values(self):
        self.authenticate(self.author)

        for body in ("", "   \n\t  ", "x" * 5001):
            response = self.post_json(reverse("community_post-list"), {"body": body})

            self.assert_error_response(
                response,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        self.assertEqual(CommunityPost.objects.count(), 0)

    def test_update_rejects_invalid_body_values(self):
        post = create_community_post(author=self.author, body="Before")
        self.authenticate(self.author)

        for body in ("", "   \n\t  ", "x" * 5001):
            response = self.patch_json(reverse("community_post-detail", args=[post.id]), {"body": body})

            self.assert_error_response(
                response,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        post.refresh_from_db()
        self.assertEqual(post.body, "Before")
