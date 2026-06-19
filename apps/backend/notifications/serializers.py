from rest_framework import serializers

from users.serializers import UserListSerializer

from .models import NotificationDelivery


class NotificationDeliverySerializer(serializers.ModelSerializer):
    reason = serializers.IntegerField(source="event.reason", read_only=True)
    channel = serializers.IntegerField(source="event.channel", read_only=True)
    actor = UserListSerializer(source="event.actor", read_only=True)
    target = serializers.SerializerMethodField()
    payload = serializers.JSONField(source="event.payload", read_only=True)

    def get_target(self, obj):
        if obj.event.target_id is None:
            return None
        return str(obj.event.target_id)

    class Meta:
        model = NotificationDelivery
        fields = (
            "id",
            "event",
            "reason",
            "channel",
            "actor",
            "target",
            "payload",
            "read_at",
            "created_at",
        )
        read_only_fields = fields
