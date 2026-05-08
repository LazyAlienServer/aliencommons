from django.db import transaction

from articles.models import PublishedArticle

from .models import Reaction, ReactionTarget


@transaction.atomic
def set_published_article_reaction(*, user, published_article: PublishedArticle, reaction_type: int):
    target, _ = ReactionTarget.objects.get_or_create(
        target_type=ReactionTarget.TargetType.PUBLISHED_ARTICLE,
        published_article=published_article,
    )
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
        target__target_type=ReactionTarget.TargetType.PUBLISHED_ARTICLE,
        target__published_article=published_article,
    ).delete()
    return deleted_count > 0

