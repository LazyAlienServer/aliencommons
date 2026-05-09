from rest_framework import serializers

from articles.models import PublishedArticle

from .models import Comment


class CommentReadSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
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
            "reply_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_published_article(self, obj):
        if obj.parent_id is not None:
            return obj.parent.target.published_article_id
        return obj.target.published_article_id

    def get_reply_count(self, obj):
        annotated_value = getattr(obj, "reply_count", None)
        if annotated_value is not None:
            return annotated_value
        return obj.replies.count()


class CommentWriteSerializer(serializers.Serializer):
    published_article = serializers.UUIDField(required=False)
    parent = serializers.UUIDField(required=False)
    body = serializers.CharField(allow_blank=False, trim_whitespace=True)

    def validate_published_article(self, value):
        try:
            return PublishedArticle.objects.get(pk=value)
        except PublishedArticle.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Published article does not exist",
                code="published_article_not_found",
            ) from exc

    def validate_parent(self, value):
        try:
            return Comment.objects.get(pk=value)
        except Comment.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Parent comment does not exist",
                code="parent_comment_not_found",
            ) from exc

    def validate_body(self, value):
        if not value:
            raise serializers.ValidationError(
                detail="Comment body cannot be blank",
                code="blank_comment_body",
            )
        return value

    def validate(self, attrs):
        parent = attrs.get("parent")
        published_article = attrs.get("published_article")

        if self.instance is not None:
            if parent is not None or published_article is not None:
                raise serializers.ValidationError(
                    detail="Comment target cannot be changed",
                    code="comment_target_immutable",
                )
            return attrs

        if parent is not None and published_article is not None:
            raise serializers.ValidationError(
                detail="Provide either parent or published_article, not both",
                code="ambiguous_comment_target",
            )

        if parent is None and published_article is None:
            raise serializers.ValidationError(
                detail="A published article or parent comment is required",
                code="comment_target_required",
            )

        if parent is not None and parent.parent_id is not None:
            raise serializers.ValidationError(
                detail="Replies cannot have replies",
                code="nested_comment_not_allowed",
            )

        return attrs
