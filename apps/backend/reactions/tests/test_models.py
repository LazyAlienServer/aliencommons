from django.db import IntegrityError, transaction

from articles.models import ArticlePublication, Article
from core.tests.factories import (
    create_content_target,
    create_article_publication,
    create_reaction,
    create_article,
    create_user,
)
from core.tests.testcases import BaseTestCase
from core.models import ContentTarget
from reactions.models import Reaction


class ReactionModelTests(BaseTestCase):
    def setUp(self):
        self.user = create_user(username="reader")
        self.article = create_article(
            status=Article.ArticleStatus.PUBLISHED,
        )
        self.published = create_article_publication(self.article)

    def test_content_target_string_representation_includes_type(self):
        target = create_content_target(self.published)

        self.assertIn("Article Publication target", str(target))

    def test_reaction_string_representation_includes_user_type_and_target(self):
        reaction = create_reaction(self.user, self.published)

        self.assertEqual(
            str(reaction),
            f"{self.user} Like {reaction.target_id}",
        )

    def test_user_can_only_have_one_reaction_per_target(self):
        target = create_content_target(self.published)
        create_reaction(self.user, self.published, target=target)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Reaction.objects.create(
                    user=self.user,
                    target=target,
                    reaction_type=Reaction.ReactionType.DISLIKE,
                )

    def test_article_publication_delete_cascades_content_target_and_reactions(self):
        target = create_content_target(self.published)
        reaction = create_reaction(self.user, self.published, target=target)

        self.published.delete()

        self.assertFalse(ArticlePublication.objects.filter(id=self.published.id).exists())
        self.assertFalse(ContentTarget.objects.filter(id=target.id).exists())
        self.assertFalse(Reaction.objects.filter(id=reaction.id).exists())

    def test_article_soft_delete_cascades_content_target_and_reactions(self):
        target = create_content_target(self.published)
        reaction = create_reaction(self.user, self.published, target=target)

        self.article.is_deleted = True
        self.article.save(update_fields=["is_deleted"])

        self.assertFalse(ArticlePublication.objects.filter(id=self.published.id).exists())
        self.assertFalse(ContentTarget.objects.filter(id=target.id).exists())
        self.assertFalse(Reaction.objects.filter(id=reaction.id).exists())
