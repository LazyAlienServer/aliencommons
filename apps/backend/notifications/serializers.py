from rest_framework import serializers

from .models import Notification


class NotificationReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for user notifications.

    Permission enforcement is handled at the ViewSet level via get_queryset(),
    which filters by recipient=request.user. This serializer only shapes the
    response data and does not perform authorization checks.
    """

    actor_id = serializers.SerializerMethodField()
    actor_type = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "verb",
            "is_read",
            "data",
            "actor_id",
            "actor_type",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_actor_id(self, obj):
        if obj.actor is None:
            return None
        return str(obj.actor.pk)

    def get_actor_type(self, obj):
        if obj.actor_content_type_id is None:
            return None
        return obj.actor_content_type.model
