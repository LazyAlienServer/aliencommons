from rest_framework import serializers

from .models import Reaction


class ReactionReadSerializer(serializers.ModelSerializer):
    target_type = serializers.IntegerField(source="target.target_type", read_only=True)
    target_type_display = serializers.CharField(source="target.get_target_type_display", read_only=True)
    published_article = serializers.UUIDField(source="target.published_article_id", read_only=True)
    reaction_type_display = serializers.CharField(source="get_reaction_type_display", read_only=True)

    class Meta:
        model = Reaction
        fields = (
            "id",
            "user",
            "target",
            "target_type",
            "target_type_display",
            "published_article",
            "reaction_type",
            "reaction_type_display",
            "created_at",
        )
        read_only_fields = fields


class ReactionWriteSerializer(serializers.Serializer):
    published_article = serializers.UUIDField(write_only=True, required=False)
    reaction_type = serializers.ChoiceField(choices=Reaction.ReactionType.choices)

    def validate_published_article(self, value):
        from articles.models import PublishedArticle

        try:
            return PublishedArticle.objects.get(pk=value)
        except PublishedArticle.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Published article does not exist",
                code="published_article_not_found",
            ) from exc

    def validate(self, attrs):
        published_article = attrs.get("published_article")

        if self.instance is None and published_article is None:
            raise serializers.ValidationError(
                detail={"published_article": "A published article is required"},
                code="published_article_required",
            )

        if self.instance is not None and published_article is not None:
            current_article_id = self.instance.target.published_article_id
            if published_article.id != current_article_id:
                raise serializers.ValidationError(
                    detail="Reaction target cannot be changed",
                    code="reaction_target_immutable",
                )

        if "reaction_type" not in attrs:
            raise serializers.ValidationError(
                detail={"reaction_type": "A reaction type is required"},
                code="reaction_type_required",
            )

        return attrs
