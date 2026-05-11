from rest_framework import serializers

from users.serializers import UserListSerializer

from .models import CommunityPost


class CommunityPostReadSerializer(serializers.ModelSerializer):
    author = UserListSerializer(read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = CommunityPost
        fields = (
            "id",
            "author",
            "author_username",
            "body",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CommunityPostWriteSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=5000, trim_whitespace=True)

    def validate_body(self, value):
        if not value:
            raise serializers.ValidationError(
                detail="Community post body cannot be blank",
                code="blank_post_body",
            )
        return value
