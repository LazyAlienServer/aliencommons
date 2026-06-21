from rest_framework import serializers

from .models import Reaction


class ReactionReadSerializer(serializers.ModelSerializer):
    target_type = serializers.IntegerField(source="target.target_type", read_only=True)
    target_type_display = serializers.CharField(source="target.get_target_type_display", read_only=True)
    article_publication = serializers.UUIDField(source="target.article_publication_id", read_only=True)
    community_post = serializers.UUIDField(source="target.community_post_id", read_only=True)
    reaction_type_display = serializers.CharField(source="get_reaction_type_display", read_only=True)

    class Meta:
        model = Reaction
        fields = (
            "id",
            "user",
            "target",
            "target_type",
            "target_type_display",
            "article_publication",
            "community_post",
            "reaction_type",
            "reaction_type_display",
            "created_at",
        )
        read_only_fields = fields


class ReactionWriteSerializer(serializers.Serializer):
    article_publication = serializers.UUIDField(write_only=True, required=False)
    community_post = serializers.UUIDField(write_only=True, required=False)
    reaction_type = serializers.ChoiceField(choices=Reaction.ReactionType.choices)

    def validate_article_publication(self, value):
        from articles.models import ArticlePublication

        try:
            return ArticlePublication.objects.get(pk=value)
        except ArticlePublication.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Article publication does not exist",
                code="article_publication_not_found",
            ) from exc

    def validate_community_post(self, value):
        from posts.models import CommunityPost

        try:
            return CommunityPost.objects.get(pk=value)
        except CommunityPost.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Community post does not exist",
                code="community_post_not_found",
            ) from exc

    def validate(self, attrs):
        article_publication = attrs.get("article_publication")
        community_post = attrs.get("community_post")

        if self.instance is None and article_publication is None and community_post is None:
            raise serializers.ValidationError(
                detail="An article publication or community post is required",
                code="reaction_target_required",
            )

        if article_publication is not None and community_post is not None:
            raise serializers.ValidationError(
                detail="Provide only one reaction target",
                code="ambiguous_reaction_target",
            )

        if self.instance is not None:
            target_changed = (
                article_publication is not None
                and article_publication.id != self.instance.target.article_publication_id
            ) or (
                community_post is not None
                and community_post.id != self.instance.target.community_post_id
            )
            if target_changed:
                raise serializers.ValidationError(
                    detail="Reaction target cannot be changed",
                    code="content_target_immutable",
                )

        if "reaction_type" not in attrs:
            raise serializers.ValidationError(
                detail={"reaction_type": "A reaction type is required"},
                code="reaction_type_required",
            )

        return attrs
