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
    article_publication_title = serializers.SerializerMethodField()
    article_id = serializers.UUIDField(source="article_publication.article_id", read_only=True)

    class Meta:
        model = Bookmark
        fields = (
            "id",
            "user",
            "folder",
            "folder_name",
            "article_publication",
            "article_publication_title",
            "article_id",
            "created_at",
        )
        read_only_fields = fields

    def get_article_publication_title(self, obj):
        latest_version = obj.article_publication.latest_version()
        return latest_version.title if latest_version else None


class BookmarkWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ("folder", "article_publication")
        validators = []

    def validate(self, attrs):
        user = self.context["request"].user
        folder = attrs.get("folder", getattr(self.instance, "folder", None))
        article_publication = attrs.get(
            "article_publication",
            getattr(self.instance, "article_publication", None),
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

        if article_publication is None:
            raise serializers.ValidationError(
                detail={"article_publication": "An article publication is required"},
                code="article_publication_required",
            )

        duplicate = Bookmark.objects.filter(
            user=user,
            article_publication=article_publication,
        )
        if self.instance is not None:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError(
                detail="This article is already bookmarked",
                code="duplicate_bookmark",
            )

        return attrs
