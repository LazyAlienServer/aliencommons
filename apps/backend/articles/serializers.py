from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

from rest_framework import serializers
from rest_framework.request import Request

from core.validators import (
    FileTypeValidator, FileSizeValidator
)
from core.utils.permissions import is_moderator
from .models import SourceArticle, PublishedArticle, ArticleSnapshot, ArticleEvent

import uuid
import io
from PIL import Image
from pathlib import Path

User = get_user_model()


class SourceArticleReadSerializer(serializers.ModelSerializer):
    """
    Serializer for moderators
    """

    author_username = serializers.CharField(source='author.username')
    status_display = serializers.SerializerMethodField()
    last_snapshot_id = serializers.SerializerMethodField()
    published_version_id = serializers.SerializerMethodField()

    class Meta:
        model = SourceArticle
        fields = '__all__'
        read_only_fields = [
            'id',
            'author',
            'title',
            'content',
            'status',
            'last_moderation_at',
            'created_at',
            'updated_at',
            'is_deleted',
            'author_username',
            'status_display',
            'last_snapshot_id',
            'published_version_id',
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

    def get_published_version_id(self, obj):
        annotated_value = getattr(obj, "published_version_id", None)
        if annotated_value is not None:
            return annotated_value

        return (
            PublishedArticle.objects
            .filter(source_article=obj)
            .values_list("id", flat=True)
            .first()
        )


class SourceArticleWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for the author, can be used to create/update
    """

    title = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=60,
        min_length=5,
        error_messages={
            'max_length': 'Title cannot be more than 60 characters',
            'min_length': 'Title cannot be less than 5 characters',
        },
    )

    class Meta:
        model = SourceArticle
        fields = ['title', 'content']

    def create(self, validated_data):
        validated_data.setdefault("title", "Untitled")
        validated_data.setdefault("content", {"type": "doc", "content": [{"type": "paragraph"}]})

        return super().create(validated_data)

    def validate_title(self, value):
        if value is not None and value.strip() == "":
            return "Untitled"

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


class PublishedArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for published articles. All fields are ready-only.
    """

    class Meta:
        model = PublishedArticle
        fields = '__all__'
        read_only_fields = (
            'id',
            'source_article',
            'title',
            'content',
            'created_at',
            'updated_at',
        )


class ArticleSnapshotSerializer(serializers.ModelSerializer):
    """
    Serializer for article snapshots. All fields are ready-only.
    """
    moderation_status_display = serializers.SerializerMethodField()
    source_article_id = serializers.SerializerMethodField()

    class Meta:
        model = ArticleSnapshot
        fields = '__all__'
        read_only_fields = (
            'id',
            'source_article',
            'title',
            'content',
            'content_hash',
            'created_at',
            'moderation_status',
            'moderation_status_display',
        )

    def get_moderation_status_display(self, obj):
        return obj.get_moderation_status_display()

    def get_source_article_id(self, obj):
        obj: ArticleSnapshot
        return obj.source_article_id


class ArticleEventSerializer(serializers.ModelSerializer):
    """
    Serializer for article moderation events. All fields are ready-only except annotation.
    """
    class Meta:
        model = ArticleEvent
        fields = '__all__'
        read_only_fields = [
            'id',
            'source_article',
            'article_snapshot',
            'annotation',
            'event_type',
            'actor',
            'created_at'
        ]

    def _get_request(self):
        req = self.context.get("request")
        return req if isinstance(req, Request) else None

    def _get_user(self):
        req = self._get_request()
        return getattr(req, "user", None)

    def get_fields(self):
        fields = super().get_fields()
        user = self._get_user()

        if is_moderator(user):
            fields['annotation'].read_only = False

        return fields

    def create(self, validated_data):
        return ArticleEvent.objects.create(**validated_data)


class ArticleActionInputSerializer(serializers.Serializer):
    """
    The input serializer for all article actions,
    which include submit, approve, reject, unpublish and delete
    """
    annotation = serializers.CharField(required=False, allow_blank=True)


class ArticleActionOutputSerializer(serializers.Serializer):
    event_type = serializers.IntegerField()
    actor_id = serializers.UUIDField()
    source_article_id = serializers.UUIDField()
    article_snapshot_id = serializers.UUIDField()
    event_id = serializers.UUIDField()

    def to_representation(self, instance):
        """
        Add event_type_display and current_status_display to the response,
        by using .label method
        """
        data = super().to_representation(instance)

        data["event_type_display"] = ArticleEvent.EventType(data["event_type"]).label

        return data
