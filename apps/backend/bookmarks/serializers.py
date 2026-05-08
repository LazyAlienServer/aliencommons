from rest_framework import serializers

from .models import Bookmark, BookmarkFolder


class BookmarkFolderReadSerializer(serializers.ModelSerializer):
    bookmark_count = serializers.SerializerMethodField()

    class Meta:
        model = BookmarkFolder
        fields = (
            "id",
            "user",
            "name",
            "bookmark_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "bookmark_count",
            "created_at",
            "updated_at",
        )

    def get_bookmark_count(self, obj):
        annotated_value = getattr(obj, "bookmark_count", None)
        if annotated_value is not None:
            return annotated_value
        return obj.bookmarks.count()


class BookmarkFolderWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, min_length=1)

    class Meta:
        model = BookmarkFolder
        fields = ("name",)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                detail="Bookmark folder name cannot be blank",
                code="blank_folder_name",
            )

        user = self.context["request"].user
        existing = BookmarkFolder.objects.filter(user=user, name=value)
        if self.instance is not None:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError(
                detail="A bookmark folder with this name already exists",
                code="duplicate_bookmark_folder_name",
            )

        return value


class BookmarkReadSerializer(serializers.ModelSerializer):
    folder_name = serializers.CharField(source="folder.name", read_only=True)
    published_article_title = serializers.CharField(source="published_article.title", read_only=True)
    source_article_id = serializers.UUIDField(source="published_article.source_article_id", read_only=True)

    class Meta:
        model = Bookmark
        fields = (
            "id",
            "user",
            "folder",
            "folder_name",
            "published_article",
            "published_article_title",
            "source_article_id",
            "created_at",
        )
        read_only_fields = fields


class BookmarkWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ("folder", "published_article")
        validators = []

    def validate(self, attrs):
        user = self.context["request"].user
        folder = attrs.get("folder", getattr(self.instance, "folder", None))
        published_article = attrs.get(
            "published_article",
            getattr(self.instance, "published_article", None),
        )

        if folder is None:
            raise serializers.ValidationError(
                detail={"folder": "A bookmark folder is required"},
                code="bookmark_folder_required",
            )

        if folder.user_id != user.id:
            raise serializers.ValidationError(
                detail="Bookmark folder must belong to the current user",
                code="bookmark_folder_not_owned",
            )

        if published_article is None:
            raise serializers.ValidationError(
                detail={"published_article": "A published article is required"},
                code="published_article_required",
            )

        duplicate = Bookmark.objects.filter(
            user=user,
            published_article=published_article,
        )
        if self.instance is not None:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError(
                detail="This article is already bookmarked",
                code="duplicate_bookmark",
            )

        return attrs
