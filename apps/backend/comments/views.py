from django.db.models import Count, Q
from rest_framework import status

from core.views.viewsets import MyModelViewSet
from .models import Comment
from .permissions import CommentPermission
from .serializers import CommentReadSerializer, CommentWriteSerializer
from .services import (
    create_comment,
    get_community_post_target,
    get_article_publication_target,
    soft_delete_comment,
    update_comment,
)


class CommentViewSet(MyModelViewSet):
    queryset = Comment.objects.select_related(
        "author",
        "target",
        "target__article_publication",
        "target__comment",
        "target__community_post",
        "parent",
        "parent__target",
    )
    permission_classes = [CommentPermission]
    default_serializer_class = CommentReadSerializer
    serializer_class_mapping = {
        "create": CommentWriteSerializer,
        "update": CommentWriteSerializer,
        "partial_update": CommentWriteSerializer,
    }

    def get_serializer_class(self):
        self.action: str
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .annotate(
                reply_count=Count(
                    "replies",
                    filter=Q(replies__is_deleted=False),
                ),
            )
        )
        article_publication_id = self.request.query_params.get("article_publication")
        community_post_id = self.request.query_params.get("community_post")
        parent_id = self.request.query_params.get("parent")

        if article_publication_id:
            target = get_article_publication_target(article_publication_id)
            if target is None:
                return queryset.none()
            queryset = queryset.filter(
                Q(target=target)
                | Q(parent__target=target)
            )

        if community_post_id:
            target = get_community_post_target(community_post_id)
            if target is None:
                return queryset.none()
            queryset = queryset.filter(
                Q(target=target)
                | Q(parent__target=target)
            )

        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        return queryset.order_by("created_at")

    def create(self, request, *args, **kwargs):
        input_serializer = CommentWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        comment = create_comment(
            author=request.user,
            body=input_serializer.validated_data["body"],
            mentions=input_serializer.validated_data["mentions"],
            article_publication=input_serializer.validated_data.get("article_publication"),
            community_post=input_serializer.validated_data.get("community_post"),
            target=input_serializer.validated_data.get("target"),
        )
        output_serializer = CommentReadSerializer(
            instance=comment,
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
        comment = self.get_object()
        input_serializer = CommentWriteSerializer(
            comment,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        comment = update_comment(
            comment=comment,
            body=input_serializer.validated_data.get("body", comment.body),
            mentions=input_serializer.validated_data.get("mentions", comment.mentions),
        )
        output_serializer = CommentReadSerializer(
            instance=comment,
            context=self.get_serializer_context(),
        )

        return self.format_success_response(
            message="updated",
            code="updated",
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        soft_delete_comment(instance)
