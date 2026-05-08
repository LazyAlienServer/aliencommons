from pathlib import Path
import io
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from PIL import Image
from rest_framework import serializers

from core.validators import (
    FileTypeValidator, FileSizeValidator
)
from core.exceptions import ServiceError
from ..models import SourceArticle, PublishedArticle, ArticleSnapshot, ArticleEvent
from ..services.markdown import extract_title_from_markdown


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
    class Meta:
        model = SourceArticle
        fields = ['markdown']

    def create(self, validated_data):
        validated_data.setdefault("markdown", str(SourceArticle.default_markdown))
        validated_data["title"] = extract_title_from_markdown(
            validated_data["markdown"],
            max_length=SourceArticle._meta.get_field("title").max_length,
        )
        return super().create(validated_data)

    def validate_markdown(self, value):
        try:
            extract_title_from_markdown(
                value,
                max_length=SourceArticle._meta.get_field("title").max_length,
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


class PublishedArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for published articles. All fields are ready-only.
    """
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = PublishedArticle
        fields = '__all__'
        read_only_fields = (
            'id',
            'source_article',
            'title',
            'html',
            'like_count',
            'dislike_count',
            'my_reaction',
            'created_at',
            'updated_at',
        )

    def get_like_count(self, obj):
        annotated_value = getattr(obj, "like_count", None)
        if annotated_value is not None:
            return annotated_value

        reaction_target = getattr(obj, "reaction_target", None)
        if reaction_target is None:
            return 0

        from reactions.models import Reaction

        return reaction_target.reactions.filter(
            reaction_type=Reaction.ReactionType.LIKE,
        ).count()

    def get_dislike_count(self, obj):
        annotated_value = getattr(obj, "dislike_count", None)
        if annotated_value is not None:
            return annotated_value

        reaction_target = getattr(obj, "reaction_target", None)
        if reaction_target is None:
            return 0

        from reactions.models import Reaction

        return reaction_target.reactions.filter(
            reaction_type=Reaction.ReactionType.DISLIKE,
        ).count()

    def get_my_reaction(self, obj):
        annotated_value = getattr(obj, "my_reaction", None)
        if annotated_value is not None:
            return annotated_value

        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return None

        reaction_target = getattr(obj, "reaction_target", None)
        if reaction_target is None:
            return None

        return (
            reaction_target.reactions
            .filter(user=request.user)
            .values_list("reaction_type", flat=True)
            .first()
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
            'markdown',
            'hash',
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
    Serializer for article moderation events.
    All fields are read-only.
    """
    class Meta:
        model = ArticleEvent
        fields = '__all__'
        read_only_fields = [
            'id',
            'source_article',
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
