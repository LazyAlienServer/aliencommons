from rest_framework import serializers

from ..models import Collection, CollectionItem


class CollectionReadSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = (
            "id",
            "author",
            "author_username",
            "title",
            "description",
            "item_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author",
            "author_username",
            "item_count",
            "created_at",
            "updated_at",
        )

    def get_item_count(self, obj):
        annotated_value = getattr(obj, "item_count", None)
        if annotated_value is not None:
            return annotated_value
        return obj.items.count()


class CollectionWriteSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, min_length=1)

    class Meta:
        model = Collection
        fields = ("title", "description")

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                detail="Collection title cannot be blank",
                code="blank_title",
            )
        return value


class CollectionItemReadSerializer(serializers.ModelSerializer):
    collection_title = serializers.CharField(source="collection.title", read_only=True)
    article_publication_title = serializers.SerializerMethodField()
    article_id = serializers.UUIDField(source="article_publication.article_id", read_only=True)

    class Meta:
        model = CollectionItem
        fields = (
            "id",
            "collection",
            "collection_title",
            "article_publication",
            "article_publication_title",
            "article_id",
            "position",
            "created_at",
        )
        read_only_fields = fields

    def get_article_publication_title(self, obj):
        latest_version = obj.article_publication.latest_version()
        return latest_version.title if latest_version else None


class CollectionItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = ("collection", "article_publication", "position")
        validators = []
        extra_kwargs = {
            "position": {"required": False},
        }

    def validate(self, attrs):
        collection = attrs.get("collection", getattr(self.instance, "collection", None))
        article_publication = attrs.get("article_publication", getattr(self.instance, "article_publication", None))

        if collection is None:
            raise serializers.ValidationError(
                detail={"collection": "A collection is required"},
                code="collection_required",
            )

        if article_publication is None:
            raise serializers.ValidationError(
                detail={"article_publication": "An article publication is required"},
                code="article_publication_required",
            )

        if article_publication.article.author_id != collection.author_id:
            raise serializers.ValidationError(
                detail="Only the collection author's articles can be added",
                code="article_publication_not_owned",
            )

        duplicate_article = CollectionItem.objects.filter(
            collection=collection,
            article_publication=article_publication,
        )
        if self.instance is not None:
            duplicate_article = duplicate_article.exclude(pk=self.instance.pk)
        if duplicate_article.exists():
            raise serializers.ValidationError(
                detail="This article is already in the collection",
                code="duplicate_collection_article",
            )

        position = attrs.get("position", getattr(self.instance, "position", None))
        if position is not None:
            duplicate_position = CollectionItem.objects.filter(
                collection=collection,
                position=position,
            )
            if self.instance is not None:
                duplicate_position = duplicate_position.exclude(pk=self.instance.pk)
            if duplicate_position.exists():
                raise serializers.ValidationError(
                    detail="This position is already used in the collection",
                    code="duplicate_collection_position",
                )

        return attrs
