from django.urls import reverse

from rest_framework import status

from core.tests.factories import (
    create_community_post,
    create_article_publication,
    create_reaction,
    create_article,
    create_user,
)
from core.tests.testcases import BaseAPITestCase
from core.models import ContentTarget
from reactions.models import Reaction


class ReactionViewTests(BaseAPITestCase):
    def setUp(self):
        self.user = create_user(username="reader")
        self.other_user = create_user(username="other-reader")
        self.article = create_article(title="Guide")
        self.published = create_article_publication(self.article, title=self.article.source.title)

    def test_user_can_like_article_publication(self):
        self.authenticate(self.user)
        response = self.post_json(
            reverse("reaction-list"),
            {
                "article_publication": str(self.published.id),
                "reaction_type": Reaction.ReactionType.LIKE,
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["user"], self.user.id)
        self.assert_uuid_equal(response.data["data"]["article_publication"], self.published.id)
        self.assertEqual(response.data["data"]["reaction_type"], Reaction.ReactionType.LIKE)
        self.assertEqual(Reaction.objects.count(), 1)
        self.assertEqual(ContentTarget.objects.count(), 1)

    def test_user_can_like_community_post(self):
        post = create_community_post(author=self.other_user, body="Post")

        self.authenticate(self.user)
        response = self.post_json(
            reverse("reaction-list"),
            {
                "community_post": str(post.id),
                "reaction_type": Reaction.ReactionType.LIKE,
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["user"], self.user.id)
        self.assert_uuid_equal(response.data["data"]["community_post"], post.id)
        self.assertIsNone(response.data["data"]["article_publication"])
        self.assertEqual(Reaction.objects.count(), 1)

    def test_posting_same_target_switches_existing_reaction(self):
        reaction = create_reaction(
            self.user,
            self.published,
            reaction_type=Reaction.ReactionType.LIKE,
        )

        self.authenticate(self.user)
        response = self.post_json(
            reverse("reaction-list"),
            {
                "article_publication": str(self.published.id),
                "reaction_type": Reaction.ReactionType.DISLIKE,
            },
        )

        reaction.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="updated",
        )
        self.assert_uuid_equal(response.data["data"]["id"], reaction.id)
        self.assertEqual(reaction.reaction_type, Reaction.ReactionType.DISLIKE)
        self.assertEqual(Reaction.objects.count(), 1)

    def test_user_only_lists_own_reactions(self):
        own_reaction = create_reaction(self.user, self.published)
        other_article = create_article(title="Other")
        other_published = create_article_publication(other_article, title=other_article.source.title)
        create_reaction(self.other_user, other_published)

        self.authenticate(self.user)
        response = self.get_json(reverse("reaction-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assert_uuid_equal(response.data["data"]["results"][0]["id"], own_reaction.id)

    def test_user_can_delete_own_reaction(self):
        reaction = create_reaction(self.user, self.published)

        self.authenticate(self.user)
        response = self.delete_json(reverse("reaction-detail", args=[reaction.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="deleted",
        )
        self.assertFalse(Reaction.objects.filter(id=reaction.id).exists())

    def test_user_can_clear_own_reaction_by_article_publication(self):
        reaction = create_reaction(self.user, self.published)

        self.authenticate(self.user)
        response = self.delete_json(
            reverse(
                "reaction-clear-article-publication",
                args=[self.published.id],
            ),
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="deleted",
        )
        self.assertTrue(response.data["data"]["deleted"])
        self.assertFalse(Reaction.objects.filter(id=reaction.id).exists())

    def test_clear_article_publication_reaction_is_idempotent(self):
        self.authenticate(self.user)
        response = self.delete_json(
            reverse(
                "reaction-clear-article-publication",
                args=[self.published.id],
            ),
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="not_reacted",
        )
        self.assertFalse(response.data["data"]["deleted"])

    def test_user_can_clear_own_reaction_by_community_post(self):
        post = create_community_post(author=self.other_user, body="Post")
        reaction = Reaction.objects.create(
            user=self.user,
            target=post.content_target,
            reaction_type=Reaction.ReactionType.LIKE,
        )

        self.authenticate(self.user)
        response = self.delete_json(
            reverse(
                "reaction-clear-community-post",
                args=[post.id],
            ),
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="deleted",
        )
        self.assertTrue(response.data["data"]["deleted"])
        self.assertFalse(Reaction.objects.filter(id=reaction.id).exists())

    def test_user_cannot_delete_another_users_reaction(self):
        reaction = create_reaction(self.other_user, self.published)

        self.authenticate(self.user)
        response = self.delete_json(reverse("reaction-detail", args=[reaction.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Reaction.objects.filter(id=reaction.id).exists())

    def test_article_publication_response_includes_reaction_counts_and_my_reaction(self):
        create_reaction(self.user, self.published, reaction_type=Reaction.ReactionType.LIKE)
        create_reaction(self.other_user, self.published, reaction_type=Reaction.ReactionType.DISLIKE)

        self.authenticate(self.user)
        response = self.get_json(reverse("article_publication-detail", args=[self.published.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="retrieved",
        )
        self.assertEqual(response.data["data"]["like_count"], 1)
        self.assertEqual(response.data["data"]["dislike_count"], 1)
        self.assertEqual(response.data["data"]["my_reaction"], Reaction.ReactionType.LIKE)
