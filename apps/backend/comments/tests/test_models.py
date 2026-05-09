from articles.models import PublishedArticle
from comments.models import Comment
from core.models import ContentTarget
from core.services.content_targets import get_or_create_published_article_target
from core.tests.factories import (
    create_comment,
    create_published_article,
    create_source_article,
    create_user,
)
from core.tests.testcases import BaseTestCase


class CommentModelTests(BaseTestCase):
    def setUp(self):
        self.author = create_user(username="commenter")
        self.article = create_source_article(title="Guide")
        self.published = create_published_article(self.article, title=self.article.title)

    def test_content_target_string_representation_includes_type(self):
        target = get_or_create_published_article_target(self.published)

        self.assertIn("Published Article target", str(target))

    def test_comment_string_representation_includes_author(self):
        comment = create_comment(self.author, self.published)

        self.assertEqual(str(comment), f"Comment {comment.id} by {self.author.id}")

    def test_comment_has_own_content_target(self):
        comment = create_comment(self.author, self.published)

        self.assertTrue(ContentTarget.objects.filter(comment=comment).exists())

    def test_published_article_delete_cascades_comments_and_comment_targets(self):
        comment = create_comment(self.author, self.published)
        comment_target = comment.content_target

        self.published.delete()

        self.assertFalse(PublishedArticle.objects.filter(id=self.published.id).exists())
        self.assertFalse(Comment.all_objects.filter(id=comment.id).exists())
        self.assertFalse(ContentTarget.objects.filter(id=comment_target.id).exists())

