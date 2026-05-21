from rest_framework import serializers
from django.db import models

from core.exceptions import ServiceError
from core.utils.markdown import (
    render_markdown_mentions,
    serialize_markdown_mentions,
    validate_markdown_mentions,
)
from users.serializers import UserListSerializer

from .models import CommunityPost


class CommunityPostReadSerializer(serializers.ModelSerializer):
    author = UserListSerializer(read_only=True)
    author_username = serializers.SerializerMethodField()
    content_target = serializers.SerializerMethodField()
    render_body = serializers.SerializerMethodField()
    mention_users = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    def get_author_username(self, obj):
        if obj.author is None:
            return None
        return obj.author.username

    def get_render_body(self, obj):
        return render_markdown_mentions(obj.body, obj.mentions)

    def get_content_target(self, obj):
        try:
            return str(obj.content_target.id)
        except CommunityPost.content_target.RelatedObjectDoesNotExist:
            return None

    def get_mention_users(self, obj):
        return serialize_markdown_mentions(obj.mentions)

    def get_like_count(self, obj):
        annotated_value = getattr(obj, "like_count", None)
        if annotated_value is not None:
            return annotated_value

        content_target = getattr(obj, "content_target", None)
        if content_target is None:
            return 0

        from reactions.models import Reaction

        return content_target.reactions.filter(
            reaction_type=Reaction.ReactionType.LIKE,
        ).count()

    def get_dislike_count(self, obj):
        annotated_value = getattr(obj, "dislike_count", None)
        if annotated_value is not None:
            return annotated_value

        content_target = getattr(obj, "content_target", None)
        if content_target is None:
            return 0

        from reactions.models import Reaction

        return content_target.reactions.filter(
            reaction_type=Reaction.ReactionType.DISLIKE,
        ).count()

    def get_my_reaction(self, obj):
        annotated_value = getattr(obj, "my_reaction", None)
        if annotated_value is not None:
            return annotated_value

        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return None

        content_target = getattr(obj, "content_target", None)
        if content_target is None:
            return None

        return (
            content_target.reactions
            .filter(user=request.user)
            .values_list("reaction_type", flat=True)
            .first()
        )

    def get_comment_count(self, obj):
        annotated_value = getattr(obj, "comment_count", None)
        if annotated_value is not None:
            return annotated_value

        content_target = getattr(obj, "content_target", None)
        if content_target is None:
            return 0

        from comments.models import Comment

        return Comment.objects.filter(
            models.Q(target=content_target)
            | models.Q(parent__target=content_target)
        ).count()

    class Meta:
        model = CommunityPost
        fields = (
            "id",
            "author",
            "author_username",
            "content_target",
            "body",
            "render_body",
            "mentions",
            "mention_users",
            "like_count",
            "dislike_count",
            "my_reaction",
            "comment_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CommunityPostWriteSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=5000, trim_whitespace=True)
    mentions = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
    )

    def validate_body(self, value):
        if not value:
            raise serializers.ValidationError(
                detail="Community post body cannot be blank",
                code="blank_post_body",
            )
        return value

    def validate(self, attrs):
        body = attrs.get("body", getattr(self.instance, "body", ""))
        mentions = attrs.get("mentions", getattr(self.instance, "mentions", []))
        try:
            attrs["mentions"] = validate_markdown_mentions(body=body, mentions=mentions)
        except ServiceError as exc:
            raise serializers.ValidationError(detail=exc.detail, code=exc.code) from exc
        return attrs
