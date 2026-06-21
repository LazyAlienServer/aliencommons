from django.db.models import Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from .models import Comment


def with_article_publication_comment_count(queryset):
    top_level_count = (
        Comment.all_objects
        .filter(
            target__article_publication_id=OuterRef("pk"),
            is_deleted=False,
        )
        .order_by()
        .values("target__article_publication")
        .annotate(count=Count("id"))
        .values("count")[:1]
    )
    reply_count = (
        Comment.all_objects
        .filter(
            parent__target__article_publication_id=OuterRef("pk"),
            is_deleted=False,
        )
        .order_by()
        .values("parent__target__article_publication")
        .annotate(count=Count("id"))
        .values("count")[:1]
    )
    return queryset.annotate(
        comment_count=(
            Coalesce(Subquery(top_level_count, output_field=IntegerField()), Value(0))
            + Coalesce(Subquery(reply_count, output_field=IntegerField()), Value(0))
        ),
    )


def with_community_post_comment_count(queryset):
    top_level_count = (
        Comment.all_objects
        .filter(
            target__community_post_id=OuterRef("pk"),
            is_deleted=False,
        )
        .order_by()
        .values("target__community_post")
        .annotate(count=Count("id"))
        .values("count")[:1]
    )
    reply_count = (
        Comment.all_objects
        .filter(
            parent__target__community_post_id=OuterRef("pk"),
            is_deleted=False,
        )
        .order_by()
        .values("parent__target__community_post")
        .annotate(count=Count("id"))
        .values("count")[:1]
    )
    return queryset.annotate(
        comment_count=(
            Coalesce(Subquery(top_level_count, output_field=IntegerField()), Value(0))
            + Coalesce(Subquery(reply_count, output_field=IntegerField()), Value(0))
        ),
    )
