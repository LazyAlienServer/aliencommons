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
    published_article_title = serializers.CharField(source="published_article.title", read_only=True)
    source_article_id = serializers.UUIDField(source="published_article.source_article_id", read_only=True)

    class Meta:
        model = CollectionItem
        fields = (
            "id",
            "collection",
            "collection_title",
            "published_article",
            "published_article_title",
            "source_article_id",
            "position",
            "created_at",
        )
        read_only_fields = fields


class CollectionItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = ("collection", "published_article", "position")
        validators = []
        extra_kwargs = {
            "position": {"required": False},
        }

    def validate(self, attrs):
        collection = attrs.get("collection", getattr(self.instance, "collection", None))
        published_article = attrs.get("published_article", getattr(self.instance, "published_article", None))

        if collection is None:
            raise serializers.ValidationError(
                detail={"collection": "A collection is required"},
                code="collection_required",
            )

        if published_article is None:
            raise serializers.ValidationError(
                detail={"published_article": "A published article is required"},
                code="published_article_required",
            )

        if published_article.source_article.author_id != collection.author_id:
            raise serializers.ValidationError(
                detail="Only the collection author's articles can be added",
                code="published_article_not_owned",
            )

        duplicate_article = CollectionItem.objects.filter(
            collection=collection,
            published_article=published_article,
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
