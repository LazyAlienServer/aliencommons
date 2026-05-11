from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.views.viewsets import MyReadOnlyModelViewSet
from .models import Notification
from .serializers import NotificationReadSerializer
from .services import (
    get_unread_count,
    mark_all_notifications_read,
    mark_notification_read,
)


class NotificationViewSet(MyReadOnlyModelViewSet):
    serializer_class = NotificationReadSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_read", "notification_type"]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(methods=["post"], detail=True)
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        mark_notification_read(notification)
        return self.format_success_response(
            message="Notification marked as read",
            code="marked_read",
            data={"id": str(notification.id), "is_read": notification.is_read},
            status_code=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False)
    def mark_all_read(self, request):
        count = mark_all_notifications_read(request.user)
        return self.format_success_response(
            message="All notifications marked as read",
            code="marked_all_read",
            data={"count": count},
            status_code=status.HTTP_200_OK,
        )

    @action(methods=["get"], detail=False)
    def unread_count(self, request):
        count = get_unread_count(request.user)
        return self.format_success_response(
            message="Unread count retrieved",
            code="unread_count",
            data={"count": count},
            status_code=status.HTTP_200_OK,
        )
