from .models import FrontendLog
from core.fields import FlexibleDateTimeField
from core.serializers import BaseSerializer, BaseModelSerializer


class SingleFrontendLogSerializer(BaseModelSerializer):
    timestamp = FlexibleDateTimeField(required=True)

    class Meta:
        model = FrontendLog
        fields = ['level', 'message', 'extra', 'timestamp', 'page']


class ListFrontendLogSerializer(BaseSerializer):
    logs = SingleFrontendLogSerializer(many=True)

    def create(self, validated_data):
        logs_data = validated_data.pop('logs')

        logs_instances = []

        for log in logs_data:
            logs_instances.append(
                FELog(
                    level=log['level'],
                    message=log['message'],
                    extra=log['extra'],
                    timestamp=log['timestamp'],
                    page=log['page']
                )
            )

        created_logs = FELog.objects.bulk_create(logs_instances)
        return created_logs
