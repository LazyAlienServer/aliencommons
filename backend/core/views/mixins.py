from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
)
from rest_framework import status

from core.responses import format_api_response


class FormattedResponseMixin:
    """
    Wrap response with format_api_response().
    """
    def format_success_response(
            self, *, message="ok", code="ok", data=None, status_code=status.HTTP_200_OK, headers=None
    ):
        request = getattr(self, 'request', None)

        return format_api_response(
            success=True,
            message=message,
            code=code,
            data=data,
            errors=None,
            status_code=status_code,
            request=request,
            headers=headers
        )


class MyCreateModelMixin(CreateModelMixin):
    """
    Create a model instance, but return a standard api response.
    This should always be used with GenericViewSet.
    """
    create_success_message = "created"
    create_success_code = 'created'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return self.format_success_response(
            message=self.create_success_message,
            code=self.create_success_code,
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
            headers=headers
        )


class MyListModelMixin(ListModelMixin):
    """
    List a queryset, but return a standard api response.
    This should always be used with GenericViewSet.
    """
    list_success_message = "listed"
    list_success_code = 'listed'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)

            return self.format_success_response(
                message=self.list_success_message,
                code=self.list_success_code,
                data=paginated_response,
                status_code=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(queryset, many=True)

        return self.format_success_response(
            message=self.list_success_message,
            code=self.list_success_code,
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class MyRetrieveModelMixin(RetrieveModelMixin):
    """
    Retrieve a model instance, but return a standard api response.
    This should always be used with GenericViewSet.
    """
    retrieve_success_message = "retrieved"
    retrieve_success_code = 'retrieved'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return self.format_success_response(
            message=self.retrieve_success_message,
            code=self.retrieve_success_code,
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class MyUpdateModelMixin(UpdateModelMixin):
    """
    Update a model instance, but return a standard api response.
    This should always be used with GenericViewSet.
    """
    update_success_message = "updated"
    update_success_code = 'updated'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return self.format_success_response(
            message=self.update_success_message,
            code=self.update_success_code,
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class MyDestroyModelMixin(DestroyModelMixin):
    """
    Destroy a model instance, but return a standard api response.
    This should always be used with GenericViewSet.
    """
    destroy_success_message = "deleted"
    destroy_success_code = 'deleted'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return self.format_success_response(
            message=self.destroy_success_message,
            code=self.destroy_success_code,
            data=None,
            status_code=status.HTTP_200_OK,
        )
