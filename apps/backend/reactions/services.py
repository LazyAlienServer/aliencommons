from django.db import transaction

from articles.models import PublishedArticle
from core.models import ContentTarget
from core.services.content_targets import (
    get_or_create_community_post_target,
    get_or_create_published_article_target,
)
from posts.models import CommunityPost

from .models import Reaction


@transaction.atomic
def set_published_article_reaction(*, user, published_article: PublishedArticle, reaction_type: int):
    target = get_or_create_published_article_target(published_article)
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


def clear_published_article_reaction(*, user, published_article: PublishedArticle):
    deleted_count, _ = Reaction.objects.filter(
        user=user,
        target__target_type=ContentTarget.TargetType.PUBLISHED_ARTICLE,
        target__published_article=published_article,
    ).delete()
    return deleted_count > 0


def clear_community_post_reaction(*, user, community_post: CommunityPost):
    deleted_count, _ = Reaction.objects.filter(
        user=user,
        target__target_type=ContentTarget.TargetType.COMMUNITY_POST,
        target__community_post=community_post,
    ).delete()
    return deleted_count > 0
