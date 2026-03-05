from rest_framework import serializers

from .models import FrontendLog
from core.fields import FlexibleDateTimeField


class SingleFrontendLogSerializer(serializers.ModelSerializer):
    timestamp = FlexibleDateTimeField(required=True)

    class Meta:
        model = FrontendLog
        fields = ['level', 'message', 'extra', 'timestamp', 'page']


class ListFrontendLogSerializer(serializers.Serializer):
    logs = SingleFrontendLogSerializer(many=True)

    def create(self, validated_data):
        logs_data = validated_data.pop('logs')

        logs_instances = []

        for log in logs_data:
            logs_instances.append(
                FrontendLog(
                    level=log['level'],
                    message=log['message'],
                    extra=log['extra'],
                    timestamp=log['timestamp'],
                    page=log['page']
                )
            )

        created_logs = FrontendLog.objects.bulk_create(logs_instances)
        return created_logs
