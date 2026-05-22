from rest_framework import serializers

from users.serializers import UserListSerializer

from .models import NotificationDelivery


class NotificationDeliverySerializer(serializers.ModelSerializer):
    event_type = serializers.IntegerField(source="event.event_type", read_only=True)
    actor = UserListSerializer(source="event.actor", read_only=True)
    target = serializers.SerializerMethodField()
    data = serializers.JSONField(source="event.data", read_only=True)

    def get_target(self, obj):
        if obj.event.target_id is None:
            return None
        return str(obj.event.target_id)

    class Meta:
        model = NotificationDelivery
        fields = (
            "id",
            "event",
            "event_type",
            "actor",
            "target",
            "data",
            "read_at",
            "created_at",
        )
        read_only_fields = fields

