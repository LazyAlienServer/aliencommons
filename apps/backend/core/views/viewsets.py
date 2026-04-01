from rest_framework.viewsets import GenericViewSet

from .mixins import (
    MyCreateModelMixin,
    MyListModelMixin,
    MyRetrieveModelMixin,
    MyUpdateModelMixin,
    MyDestroyModelMixin,
    FormattedResponseMixin
)


class MyModelViewSet(MyCreateModelMixin,
                     MyListModelMixin,
                     MyRetrieveModelMixin,
                     MyUpdateModelMixin,
                     MyDestroyModelMixin,
                     FormattedResponseMixin,
                     GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    Responses are wrapped with format_api_response().
    This viewset should always be used to replace drf ModelViewSet.
    """

    pass


class MyReadOnlyModelViewSet(MyListModelMixin, MyRetrieveModelMixin, FormattedResponseMixin, GenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    Responses are wrapped with format_api_response().
    This viewset should always be used to replace drf ReadOnlyModelViewSet.
    """

    pass
