from articles.models import ArticlePublication
from comments.models import Comment
from core.models import ContentTarget
from core.services.content_targets import get_or_create_article_publication_target
from core.tests.factories import (
    create_comment,
    create_article_publication,
    create_article,
    create_user,
)
from core.tests.testcases import BaseTestCase


class CommentModelTests(BaseTestCase):
    def setUp(self):
        self.author = create_user(username="commenter")
        self.article = create_article(title="Guide")
        self.published = create_article_publication(self.article, title=self.article.source.title)

    def test_content_target_string_representation_includes_type(self):
        target = get_or_create_article_publication_target(self.published)

        self.assertIn("Article Publication target", str(target))

    def test_comment_string_representation_includes_author(self):
        comment = create_comment(self.author, self.published)

        self.assertEqual(str(comment), f"Comment {comment.id} by {self.author.id}")

    def test_comment_has_own_content_target(self):
        comment = create_comment(self.author, self.published)

        self.assertTrue(ContentTarget.objects.filter(comment=comment).exists())

    def test_comment_created_directly_has_content_target(self):
        target = get_or_create_article_publication_target(self.published)

        comment = Comment.objects.create(
            author=self.author,
            target=target,
            body="Direct",
        )

        self.assertEqual(comment.content_target.target_type, ContentTarget.TargetType.COMMENT)
        self.assertEqual(comment.content_target.comment, comment)

    def test_article_publication_delete_cascades_comments_and_comment_targets(self):
        comment = create_comment(self.author, self.published)
        comment_target = comment.content_target

        self.published.delete()

        self.assertFalse(ArticlePublication.objects.filter(id=self.published.id).exists())
        self.assertFalse(Comment.all_objects.filter(id=comment.id).exists())
        self.assertFalse(ContentTarget.objects.filter(id=comment_target.id).exists())
