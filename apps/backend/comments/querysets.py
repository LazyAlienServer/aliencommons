from django.db.models import Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from .models import Comment


def with_published_article_comment_count(queryset):
    top_level_count = (
        Comment.all_objects
        .filter(
            target__published_article_id=OuterRef("pk"),
            is_deleted=False,
        )
        .order_by()
        .values("target__published_article")
        .annotate(count=Count("id"))
        .values("count")[:1]
    )
    reply_count = (
        Comment.all_objects
        .filter(
            parent__target__published_article_id=OuterRef("pk"),
            is_deleted=False,
        )
        .order_by()
        .values("parent__target__published_article")
        .annotate(count=Count("id"))
        .values("count")[:1]
    )
    return queryset.annotate(
        comment_count=(
            Coalesce(Subquery(top_level_count, output_field=IntegerField()), Value(0))
            + Coalesce(Subquery(reply_count, output_field=IntegerField()), Value(0))
        ),
    )
