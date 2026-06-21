from django.db import transaction

from articles.models import ArticlePublication
from core.models import ContentTarget
from core.services.content_targets import (
    get_or_create_community_post_target,
    get_or_create_article_publication_target,
)
from posts.models import CommunityPost

from .models import Reaction


@transaction.atomic
def set_article_publication_reaction(*, user, article_publication: ArticlePublication, reaction_type: int):
    target = get_or_create_article_publication_target(article_publication)
    reaction, created = Reaction.objects.update_or_create(
        user=user,
        target=target,
        defaults={"reaction_type": reaction_type},
    )
    return reaction, created


@transaction.atomic
def set_community_post_reaction(*, user, community_post: CommunityPost, reaction_type: int):
    target = get_or_create_community_post_target(community_post)
    reaction, created = Reaction.objects.update_or_create(
        user=user,
        target=target,
        defaults={"reaction_type": reaction_type},
    )
    return reaction, created


def update_reaction_type(*, reaction: Reaction, reaction_type: int):
    reaction.reaction_type = reaction_type
    reaction.save(update_fields=["reaction_type"])
    return reaction


def clear_article_publication_reaction(*, user, article_publication: ArticlePublication):
    deleted_count, _ = Reaction.objects.filter(
        user=user,
        target__target_type=ContentTarget.TargetType.ARTICLE_PUBLICATION,
        target__article_publication=article_publication,
    ).delete()
    return deleted_count > 0


def clear_community_post_reaction(*, user, community_post: CommunityPost):
    deleted_count, _ = Reaction.objects.filter(
        user=user,
        target__target_type=ContentTarget.TargetType.COMMUNITY_POST,
        target__community_post=community_post,
    ).delete()
    return deleted_count > 0
