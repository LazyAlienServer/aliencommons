import logging

from django.core import signals
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    NotFound,
    PermissionDenied as DRFPermissionDenied,
    ValidationError,
)

from .exceptions import ServiceError
from .formatters import ErrorFormatter
from .responses import format_response
from .settings import import_from_setting

logger = logging.getLogger(__name__)


class ExceptionHandler:
    """
    Wrap DRF, Django, and service-layer exceptions in the standard payload.
    """

    def __init__(self, formatter=None):
        self.formatter = formatter or ErrorFormatter()

    def __call__(self, exc, context):
        return self.handle(exc, context)

    def handle(self, exc, context):
        request = context.get("request")
        exc = self.convert_known_exceptions(exc)

        if isinstance(exc, ServiceError):
            return self.handle_service_error(exc, request)

        if isinstance(exc, ValidationError):
            return self.handle_validation_error(exc, request)

        from rest_framework.views import exception_handler as drf_exception_handler

        response = drf_exception_handler(exc, context)

        if response is None:
            return self.handle_unhandled_error(exc, request)

        return self.handle_api_error(exc, response, request)

    def convert_known_exceptions(self, exc):
        if isinstance(exc, Http404):
            return NotFound()
        if isinstance(exc, PermissionDenied):
            return DRFPermissionDenied()
        return exc

    def handle_service_error(self, exc, request):
        message = str(getattr(exc, "detail", "Request failed"))
        code = str(getattr(exc, "code", "request_failed"))
        status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)

        logger.warning("Service Error: %s", message)

        return format_response(
            success=False,
            message=message,
            code=code,
            data=None,
            errors=[
                self.formatter.format_error(
                    code=code,
                    message=message,
                    field=None,
                )
            ],
            request=request,
            status_code=status_code,
        )

    def handle_validation_error(self, exc, request):
        status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)

        logger.warning("Validation Error")

        return format_response(
            success=False,
            message="Validation failed",
            code="validation_error",
            data=None,
            errors=self.formatter.format_errors(exc.detail),
            request=request,
            status_code=status_code,
        )

    def handle_unhandled_error(self, exc, request):
        logger.error(
            "Unknown exception",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        signals.got_request_exception.send(sender=None, request=request)

        return format_response(
            success=False,
            message="Internal server error",
            code="internal_server_error",
            data=None,
            errors=[
                self.formatter.format_error(
                    code="internal_server_error",
                    message="Internal server error",
                    field=None,
                )
            ],
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def handle_api_error(self, exc, response, request):
        code = self.get_exception_code(exc)

        return format_response(
            success=False,
            message="Request failed",
            code=code,
            data=None,
            errors=self.formatter.format_errors(response.data),
            request=request,
            status_code=response.status_code,
            headers=response.headers,
        )

    def get_exception_code(self, exc):
        if isinstance(exc, APIException):
            return getattr(exc, "default_code", "error")
        return "error"


def exception_handler(exc, context):
    handler_class = import_from_setting("EXCEPTION_HANDLER_CLASS")
    formatter_class = import_from_setting("EXCEPTION_FORMATTER_CLASS")
    return handler_class(formatter=formatter_class())(exc, context)
