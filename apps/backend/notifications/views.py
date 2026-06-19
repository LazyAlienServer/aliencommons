from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.exceptions import ServiceError
from core.views.viewsets import MyReadOnlyModelViewSet

from .models import NotificationDelivery, NotificationEvent
from .serializers import NotificationDeliverySerializer
from .services import mark_all_deliveries_read, mark_delivery_read


class NotificationDeliveryViewSet(MyReadOnlyModelViewSet):
    serializer_class = NotificationDeliverySerializer
    permission_classes = [IsAuthenticated]
    queryset = NotificationDelivery.objects.select_related(
        "recipient",
        "event",
        "event__actor",
        "event__target",
    )

    def get_queryset(self):
        queryset = super().get_queryset().filter(recipient=self.request.user)
        channel = self.request.query_params.get("channel")
        if channel:
            try:
                channel_value = NotificationEvent.Channel[channel.upper()]
            except KeyError as exc:
                raise ServiceError(
                    detail="Invalid notification channel",
                    code="invalid_notification_channel",
                ) from exc
            queryset = queryset.filter(event__channel=channel_value)
        return queryset

    @action(detail=False, methods=["get"], url_path="unread_count")
    def unread_count(self, request):
        count = self.get_queryset().filter(read_at__isnull=True).count()
        return self.format_success_response(
            message="retrieved",
            code="unread_count_retrieved",
            data={"count": count},
        )

    @action(detail=True, methods=["post"], url_path="mark_read")
    def mark_read(self, request, pk=None):
        delivery = mark_delivery_read(self.get_object())
        serializer = self.get_serializer(delivery)
        return self.format_success_response(
            message="updated",
            code="marked_read",
            data=serializer.data,
        )

    @action(detail=False, methods=["post"], url_path="mark_all_read")
    def mark_all_read(self, request):
        updated = mark_all_deliveries_read(recipient=request.user)
        return self.format_success_response(
            message="updated",
            code="marked_all_read",
            data={"updated": updated},
            status_code=status.HTTP_200_OK,
        )
