from django.db.models import Count
from rest_framework import status

from core.views.viewsets import MyModelViewSet
from .models import Bookmark, BookmarkFolder
from .permissions import BookmarkOwnerOnly
from .serializers import (
    BookmarkFolderReadSerializer,
    BookmarkFolderWriteSerializer,
    BookmarkReadSerializer,
    BookmarkWriteSerializer,
)


class BookmarkFolderViewSet(MyModelViewSet):
    queryset = BookmarkFolder.objects.select_related("user")
    permission_classes = [BookmarkOwnerOnly]
    default_serializer_class = BookmarkFolderReadSerializer

    serializer_class_mapping = {
        "create": BookmarkFolderWriteSerializer,
        "update": BookmarkFolderWriteSerializer,
        "partial_update": BookmarkFolderWriteSerializer,
    }

    def get_serializer_class(self):
        self.action: str
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .annotate(bookmark_count=Count("bookmarks"))
            .order_by("created_at")
        )

    def create(self, request, *args, **kwargs):
        input_serializer = BookmarkFolderWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        folder = input_serializer.save(user=request.user)
        output_serializer = BookmarkFolderReadSerializer(
            instance=folder,
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
        folder = self.get_object()
        input_serializer = BookmarkFolderWriteSerializer(
            folder,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        folder = input_serializer.save()
        output_serializer = BookmarkFolderReadSerializer(
            instance=folder,
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


class BookmarkViewSet(MyModelViewSet):
    queryset = Bookmark.objects.select_related(
        "user",
        "folder",
        "published_article",
        "published_article__source_article",
    )
    permission_classes = [BookmarkOwnerOnly]
    default_serializer_class = BookmarkReadSerializer

    serializer_class_mapping = {
        "create": BookmarkWriteSerializer,
        "update": BookmarkWriteSerializer,
        "partial_update": BookmarkWriteSerializer,
    }

    def get_serializer_class(self):
        self.action: str
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        folder_id = self.request.query_params.get("folder")
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        return queryset

    def create(self, request, *args, **kwargs):
        input_serializer = BookmarkWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        bookmark = input_serializer.save(user=request.user)
        output_serializer = BookmarkReadSerializer(
            instance=bookmark,
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
        bookmark = self.get_object()
        input_serializer = BookmarkWriteSerializer(
            bookmark,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        bookmark = input_serializer.save()
        output_serializer = BookmarkReadSerializer(
            instance=bookmark,
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
