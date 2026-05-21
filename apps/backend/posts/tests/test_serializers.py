from rest_framework.exceptions import ErrorDetail

from core.tests.factories import create_community_post, create_user
from core.tests.testcases import BaseTestCase
from posts.serializers import CommunityPostReadSerializer, CommunityPostWriteSerializer


class CommunityPostSerializerTests(BaseTestCase):
    def test_write_serializer_rejects_blank_body(self):
        serializer = CommunityPostWriteSerializer(data={"body": ""})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["body"],
            [ErrorDetail(string="This field may not be blank.", code="blank")],
        )

    def test_write_serializer_rejects_whitespace_only_body(self):
        serializer = CommunityPostWriteSerializer(data={"body": "   \n\t  "})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["body"],
            [ErrorDetail(string="This field may not be blank.", code="blank")],
        )

    def test_write_serializer_rejects_body_over_5000_characters(self):
        serializer = CommunityPostWriteSerializer(data={"body": "x" * 5001})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["body"][0].code, "max_length")

    def test_write_serializer_accepts_and_trims_valid_body(self):
        serializer = CommunityPostWriteSerializer(data={"body": "  Hello community  "})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["body"], "Hello community")

    def test_read_serializer_exposes_author_username(self):
        author = create_user(username="post-author")
        post = create_community_post(author=author, body="Hello community")

        data = CommunityPostReadSerializer(post).data

        self.assertEqual(data["author_username"], "post-author")
        self.assertEqual(data["author"]["username"], "post-author")
        self.assertEqual(data["content_target"], str(post.content_target.id))

    def test_write_serializer_validates_mentions(self):
        mentioned = create_user(username="mentioned")
        serializer = CommunityPostWriteSerializer(
            data={
                "body": "Hello {{mention:0}}",
                "mentions": [str(mentioned.id)],
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["mentions"], [str(mentioned.id)])

    def test_write_serializer_rejects_unused_mentions(self):
        mentioned = create_user(username="mentioned")
        serializer = CommunityPostWriteSerializer(
            data={
                "body": "Hello community",
                "mentions": [str(mentioned.id)],
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"][0].code, "unused_mention")
