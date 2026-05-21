from django.db.models import Count, OuterRef, Q, Subquery

from .models import Reaction


def with_published_article_reaction_summary(queryset, *, user=None):
    queryset = queryset.annotate(
        like_count=Count(
            "content_target__reactions",
            filter=Q(
                content_target__reactions__reaction_type=Reaction.ReactionType.LIKE,
            ),
        ),
        dislike_count=Count(
            "content_target__reactions",
            filter=Q(
                content_target__reactions__reaction_type=Reaction.ReactionType.DISLIKE,
            ),
        ),
    )

    if user and user.is_authenticated:
        my_reaction = (
            Reaction.objects
            .filter(
                user=user,
                target__published_article_id=OuterRef("pk"),
            )
            .values("reaction_type")[:1]
        )
        queryset = queryset.annotate(my_reaction=Subquery(my_reaction))

    return queryset


def with_community_post_reaction_summary(queryset, *, user=None):
    queryset = queryset.annotate(
        like_count=Count(
            "content_target__reactions",
            filter=Q(
                content_target__reactions__reaction_type=Reaction.ReactionType.LIKE,
            ),
        ),
        dislike_count=Count(
            "content_target__reactions",
            filter=Q(
                content_target__reactions__reaction_type=Reaction.ReactionType.DISLIKE,
            ),
        ),
    )

    if user and user.is_authenticated:
        my_reaction = (
            Reaction.objects
            .filter(
                user=user,
                target__community_post_id=OuterRef("pk"),
            )
            .values("reaction_type")[:1]
        )
        queryset = queryset.annotate(my_reaction=Subquery(my_reaction))

    return queryset
