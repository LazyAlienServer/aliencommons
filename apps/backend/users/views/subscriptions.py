from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.views.viewsets import MyModelViewSet
from ..models import UserSubscription
from ..serializers import UserSubscriptionReadSerializer, UserSubscriptionWriteSerializer


class UserSubscriptionViewSet(MyModelViewSet):
    queryset = UserSubscription.objects.select_related("subscriber", "subscribed_to")
    permission_classes = [IsAuthenticated]
    default_serializer_class = UserSubscriptionReadSerializer

    serializer_class_mapping = {
        "create": UserSubscriptionWriteSerializer,
    }

    def get_serializer_class(self):
        self.action: str
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(subscriber=self.request.user)
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        input_serializer = UserSubscriptionWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        subscription = input_serializer.save(subscriber=request.user)
        output_serializer = UserSubscriptionReadSerializer(
            instance=subscription,
            context=self.get_serializer_context(),
        )

        return self.format_success_response(
            message="created",
            code="created",
            data=output_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )
