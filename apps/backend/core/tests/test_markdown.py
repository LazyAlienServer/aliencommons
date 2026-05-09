from core.exceptions import ServiceError
from core.tests.factories import create_user
from core.tests.testcases import BaseTestCase
from core.utils.markdown import (
    extract_title_from_markdown,
    render_markdown_mentions,
    serialize_markdown_mentions,
    validate_article_markdown,
    validate_markdown_mentions,
)


class MarkdownUtilityTests(BaseTestCase):
    def test_extract_title_from_first_line_h1(self):
        title = extract_title_from_markdown("# Title\n\nBody")

        self.assertEqual(title, "Title")

    def test_validate_article_markdown_rejects_multiple_h1_headings(self):
        with self.assertRaises(ServiceError) as exc:
            validate_article_markdown("# Title\n\n# Another")

        self.assertEqual(exc.exception.code, "invalid_article_markdown")

    def test_validate_markdown_mentions_returns_user_ids(self):
        user = create_user(username="mentioned")

        mentions = validate_markdown_mentions(
            body="{{mention:0}} hello",
            mentions=[user.id],
        )

        self.assertEqual(mentions, [str(user.id)])

    def test_validate_markdown_mentions_rejects_unused_mentions(self):
        user = create_user(username="mentioned")

        with self.assertRaises(ServiceError) as exc:
            validate_markdown_mentions(
                body="hello",
                mentions=[user.id],
            )

        self.assertEqual(exc.exception.code, "unused_mention")

    def test_render_markdown_mentions_uses_current_username(self):
        user = create_user(username="current-name")

        rendered = render_markdown_mentions(
            "{{mention:0}} hello",
            [user.id],
        )

        self.assertEqual(
            rendered,
            "[@current-name](http://testserver/users/current-name) hello",
        )

    def test_serialize_markdown_mentions_returns_current_usernames(self):
        user = create_user(username="current-name")

        mentions = serialize_markdown_mentions([user.id])

        self.assertEqual(
            mentions,
            [
                {
                    "user_id": str(user.id),
                    "username": "current-name",
                },
            ],
        )
