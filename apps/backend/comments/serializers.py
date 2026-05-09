from rest_framework import serializers

from articles.models import PublishedArticle
from core.exceptions import ServiceError
from core.models import ContentTarget
from core.utils.markdown import (
    render_markdown_mentions,
    serialize_markdown_mentions,
    validate_markdown_mentions,
)

from .models import Comment


class CommentReadSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    render_body = serializers.SerializerMethodField()
    mention_users = serializers.SerializerMethodField()
    published_article = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "author_username",
            "target",
            "published_article",
            "parent",
            "body",
            "render_body",
            "mentions",
            "mention_users",
            "reply_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_published_article(self, obj):
        if obj.parent_id is not None:
            return obj.parent.target.published_article_id
        return obj.target.published_article_id

    def get_render_body(self, obj):
        return render_markdown_mentions(obj.body, obj.mentions)

    def get_mention_users(self, obj):
        return serialize_markdown_mentions(obj.mentions)

    def get_reply_count(self, obj):
        annotated_value = getattr(obj, "reply_count", None)
        if annotated_value is not None:
            return annotated_value
        return obj.replies.count()


class CommentWriteSerializer(serializers.Serializer):
    published_article = serializers.UUIDField(required=False)
    target = serializers.UUIDField(required=False)
    body = serializers.CharField(allow_blank=False, trim_whitespace=True)
    mentions = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
    )

    def validate_published_article(self, value):
        try:
            return PublishedArticle.objects.get(pk=value)
        except PublishedArticle.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Published article does not exist",
                code="published_article_not_found",
            ) from exc

    def validate_target(self, value):
        try:
            return ContentTarget.objects.select_related("comment").get(pk=value)
        except ContentTarget.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Content target does not exist",
                code="content_target_not_found",
            ) from exc

    def validate_body(self, value):
        if not value:
            raise serializers.ValidationError(
                detail="Comment body cannot be blank",
                code="blank_comment_body",
            )
        return value

    def validate(self, attrs):
        target = attrs.get("target")
        published_article = attrs.get("published_article")
        body = attrs.get("body", getattr(self.instance, "body", ""))
        mentions = attrs.get("mentions", getattr(self.instance, "mentions", []))
        try:
            attrs["mentions"] = validate_markdown_mentions(body=body, mentions=mentions)
        except ServiceError as exc:
            raise serializers.ValidationError(detail=exc.detail, code=exc.code) from exc

        if self.instance is not None:
            if target is not None or published_article is not None:
                raise serializers.ValidationError(
                    detail="Comment target cannot be changed",
                    code="comment_target_immutable",
                )
            return attrs

        if target is not None and published_article is not None:
            raise serializers.ValidationError(
                detail="Provide either target or published_article, not both",
                code="ambiguous_comment_target",
            )

        if target is None and published_article is None:
            raise serializers.ValidationError(
                detail="A published article or content target is required",
                code="comment_target_required",
            )

        if target is not None and target.comment_id is None:
            raise serializers.ValidationError(
                detail="Replies must target a comment",
                code="invalid_comment_reply_target",
            )

        return attrs
