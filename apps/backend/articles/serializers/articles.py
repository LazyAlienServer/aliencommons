from pathlib import Path
import io
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from PIL import Image
from rest_framework import serializers

from core.validators import (
    FileTypeValidator, FileSizeValidator
)
from core.exceptions import ServiceError
from ..models import (
    Article,
    ArticleSource,
    ArticlePublication,
    ArticlePublicationVersion,
    ArticleSnapshot,
    ArticleEvent,
)
from ..services.markdown import extract_title_from_markdown


User = get_user_model()


class ArticleReadSerializer(serializers.ModelSerializer):
    """
    Serializer for moderators
    """
    author_username = serializers.CharField(source='author.username')
    title = serializers.CharField(source="source.title", read_only=True)
    markdown = serializers.CharField(source="source.markdown", read_only=True)
    version = serializers.IntegerField(source="source.version", read_only=True)
    status_display = serializers.SerializerMethodField()
    last_snapshot_id = serializers.SerializerMethodField()
    publication_id = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "author",
            "title",
            "markdown",
            "version",
            "status",
            "last_saved_at",
            "last_moderation_at",
            "created_at",
            "updated_at",
            "is_deleted",
            "author_username",
            "status_display",
            "last_snapshot_id",
            "publication_id",
        )
        read_only_fields = [
            'id',
            'author',
            'title',
            'markdown',
            'version',
            'status',
            'last_saved_at',
            'last_moderation_at',
            'created_at',
            'updated_at',
            'is_deleted',
            'author_username',
            'status_display',
            'last_snapshot_id',
            'publication_id',
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_last_snapshot_id(self, obj):
        annotated_value = getattr(obj, "last_snapshot_id", None)
        if annotated_value is not None:
            return annotated_value

        last_snapshot_id = (
            obj.article_snapshots
            .order_by("-created_at")
            .values_list("id", flat=True)
            .first()
        )
        return last_snapshot_id

    def get_publication_id(self, obj):
        annotated_value = getattr(obj, "publication_id", None)
        if annotated_value is not None:
            return annotated_value

        return (
            ArticlePublication.objects
            .filter(article=obj)
            .values_list("id", flat=True)
            .first()
        )


class ArticleWriteSerializer(serializers.Serializer):
    """
    Serializer for the author, can be used to create/update
    """
    markdown = serializers.CharField(required=False, allow_blank=True)

    def validate_markdown(self, value):
        try:
            extract_title_from_markdown(
                value,
                max_length=ArticleSource._meta.get_field("title").max_length,
            )
        except ServiceError as exc:
            raise serializers.ValidationError(detail=exc.detail, code=exc.code)
        return value


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(
        validators=[
            FileSizeValidator(object_display_name="image", max_size_mb=4),
            FileTypeValidator(object_display_name="image")
        ]
    )

    def create(self, validated_data):
        image = validated_data['image']

        image = Image.open(image)
        image = image.convert("RGB")
        image.thumbnail((1600, 1600))
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=85)
        webp_file = ContentFile(buffer.getvalue())

        file_name = f"{uuid.uuid4().hex}.webp"
        rel_dir = Path('article_images') / str(timezone.now().year) / f"{timezone.now().month:02d}"
        rel_path = str(rel_dir / file_name)

        saved_path = default_storage.save(rel_path, webp_file)
        url = default_storage.url(saved_path)

        return {
            'url': url,
            "path": saved_path,
            "name": Path(saved_path).name,
        }


class ArticlePublicationVersionSerializer(serializers.ModelSerializer):
    """
    Serializer for immutable article publication versions.
    """

    class Meta:
        model = ArticlePublicationVersion
        fields = (
            "id",
            "approved_snapshot",
            "version",
            "title",
            "html",
            "publication_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ArticlePublicationSerializer(serializers.ModelSerializer):
    """
    Serializer for article publications. All fields are ready-only.
    """
    latest_version = serializers.SerializerMethodField()
    versions = ArticlePublicationVersionSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()
    html = serializers.SerializerMethodField()
    publication_at = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = ArticlePublication
        fields = (
            "id",
            "article",
            "latest_version",
            "versions",
            "title",
            "html",
            "publication_at",
            "published_at",
            "like_count",
            "dislike_count",
            "my_reaction",
            "comment_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            'id',
            'article',
            'latest_version',
            'versions',
            'title',
            'html',
            'publication_at',
            'published_at',
            'like_count',
            'dislike_count',
            'my_reaction',
            'comment_count',
            'created_at',
            'updated_at',
        )

    def _get_latest_version(self, obj):
        return obj.latest_version()

    def get_latest_version(self, obj):
        latest_version = self._get_latest_version(obj)
        if latest_version is None:
            return None
        return ArticlePublicationVersionSerializer(latest_version).data

    def get_title(self, obj):
        latest_version = self._get_latest_version(obj)
        return latest_version.title if latest_version else None

    def get_html(self, obj):
        latest_version = self._get_latest_version(obj)
        return latest_version.html if latest_version else None

    def get_publication_at(self, obj):
        latest_version = self._get_latest_version(obj)
        return latest_version.publication_at if latest_version else None

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

class ArticleSnapshotSerializer(serializers.ModelSerializer):
    """
    Serializer for article snapshots. All fields are ready-only.
    """
    moderation_status_display = serializers.SerializerMethodField()
    article_id = serializers.SerializerMethodField()

    class Meta:
        model = ArticleSnapshot
        fields = '__all__'
        read_only_fields = (
            'id',
            'article',
            'title',
            'markdown',
            'hash',
            'created_at',
            'moderation_status',
            'moderation_status_display',
        )

    def get_moderation_status_display(self, obj):
        return obj.get_moderation_status_display()

    def get_article_id(self, obj):
        obj: ArticleSnapshot
        return obj.article_id


class ArticleEventSerializer(serializers.ModelSerializer):
    """
    Serializer for article moderation events.
    All fields are read-only.
    """
    class Meta:
        model = ArticleEvent
        fields = '__all__'
        read_only_fields = [
            'id',
            'article',
            'article_snapshot',
            'event_type',
            'actor',
            'created_at'
        ]

    def create(self, validated_data):
        return ArticleEvent.objects.create(**validated_data)


class ArticleActionResponseSerializer(serializers.Serializer):
    event_type = serializers.IntegerField()
    actor_id = serializers.UUIDField()
    article_id = serializers.UUIDField()
    article_snapshot_id = serializers.UUIDField(allow_null=True)
    event_id = serializers.UUIDField()

    def to_representation(self, instance):
        """
        Add event_type_display and current_status_display to the response,
        by using .label method
        """
        data = super().to_representation(instance)

        data["event_type_display"] = ArticleEvent.EventType(data["event_type"]).label

        return data
