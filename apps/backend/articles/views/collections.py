from django.db.models import Count, Max
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from core.views.viewsets import MyModelViewSet
from ..models import Collection, CollectionItem
from ..permissions import CollectionItemPermission, CollectionPermission
from ..serializers import (
    CollectionItemReadSerializer,
    CollectionItemWriteSerializer,
    CollectionReadSerializer,
    CollectionWriteSerializer,
)


class CollectionViewSet(MyModelViewSet):
    queryset = Collection.objects.select_related("author")
    permission_classes = [CollectionPermission]
    default_serializer_class = CollectionReadSerializer

    serializer_class_mapping = {
        "create": CollectionWriteSerializer,
        "update": CollectionWriteSerializer,
        "partial_update": CollectionWriteSerializer,
    }

    def get_serializer_class(self):
        self.action: str
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(item_count=Count("items"))
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        input_serializer = CollectionWriteSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        collection = input_serializer.save(author=request.user)
        output_serializer = CollectionReadSerializer(
            instance=collection,
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
        collection = self.get_object()
        input_serializer = CollectionWriteSerializer(
            collection,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        collection = input_serializer.save()

        output_serializer = CollectionReadSerializer(
            instance=collection,
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


class CollectionItemViewSet(MyModelViewSet):
    queryset = CollectionItem.objects.select_related(
        "collection",
        "collection__author",
        "article_publication",
        "article_publication__article",
    )
    permission_classes = [CollectionItemPermission]
    default_serializer_class = CollectionItemReadSerializer

    serializer_class_mapping = {
        "create": CollectionItemWriteSerializer,
        "update": CollectionItemWriteSerializer,
        "partial_update": CollectionItemWriteSerializer,
    }

    def get_serializer_class(self):
        self.action: str
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        queryset = super().get_queryset()
        collection_id = self.request.query_params.get("collection")
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)

        return queryset

    def _assert_collection_author(self, collection):
        if collection.author_id != self.request.user.id:
            raise PermissionDenied("Only the collection author can manage collection items")

    def _fill_position(self, validated_data):
        if "position" in validated_data:
            return validated_data

        collection = validated_data["collection"]
        last_position = (
            CollectionItem.objects
            .filter(collection=collection)
            .aggregate(last_position=Max("position"))
            .get("last_position")
        )
        validated_data["position"] = 1 if last_position is None else last_position + 1

        return validated_data

    def create(self, request, *args, **kwargs):
        input_serializer = CollectionItemWriteSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = self._fill_position(dict(input_serializer.validated_data))
        self._assert_collection_author(validated_data["collection"])

        collection_item = CollectionItem.objects.create(**validated_data)
        output_serializer = CollectionItemReadSerializer(
            instance=collection_item,
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
        collection_item = self.get_object()
        input_serializer = CollectionItemWriteSerializer(
            collection_item,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        self._assert_collection_author(
            input_serializer.validated_data.get("collection", collection_item.collection)
        )
        collection_item = input_serializer.save()

        output_serializer = CollectionItemReadSerializer(
            instance=collection_item,
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
