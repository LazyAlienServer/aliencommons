from rest_framework import status

from core.views.viewsets import MyModelViewSet

from .models import CommunityPost
from .permissions import CommunityPostPermission
from .serializers import CommunityPostReadSerializer, CommunityPostWriteSerializer
from .services import (
    create_community_post,
    soft_delete_community_post,
    update_community_post,
)


class CommunityPostViewSet(MyModelViewSet):
    queryset = CommunityPost.objects.filter(is_deleted=False).select_related("author").order_by("-created_at")
    permission_classes = [CommunityPostPermission]
    default_serializer_class = CommunityPostReadSerializer
    serializer_class_mapping = {
        "create": CommunityPostWriteSerializer,
        "update": CommunityPostWriteSerializer,
        "partial_update": CommunityPostWriteSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def create(self, request, *args, **kwargs):
        serializer = CommunityPostWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        post = create_community_post(
            author=request.user,
            **serializer.validated_data,
        )
        output_serializer = CommunityPostReadSerializer(
            instance=post,
            context=self.get_serializer_context(),
        )

        return self.format_success_response(
            message="created",
            code="created",
            data=output_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        post = self.get_object()
        serializer = CommunityPostWriteSerializer(
            post,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        post = update_community_post(
            post=post,
            **serializer.validated_data,
        )
        output_serializer = CommunityPostReadSerializer(
            instance=post,
            context=self.get_serializer_context(),
        )

        return self.format_success_response(
            message="updated",
            code="updated",
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        soft_delete_community_post(post=post)

        return self.format_success_response(
            message="deleted",
            code="deleted",
            status_code=status.HTTP_204_NO_CONTENT,
        )
