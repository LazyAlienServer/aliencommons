import logging

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError

from .exceptions import ServiceError
from .responses import format_response

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    """
    Wrap DRF, Django, and service-layer exceptions in the standard payload.
    """
    request = context.get("request")

    if isinstance(exc, ServiceError):
        message = str(getattr(exc, "detail", "Request failed"))
        code = str(getattr(exc, "code", "request_failed"))
        status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)

        logger.warning("Service Error: %s", message)

        return format_response(
            success=False,
            message=message,
            code=code,
            data=None,
            errors=None,
            request=request,
            status_code=status_code,
        )

    if isinstance(exc, ValidationError):
        code = str(getattr(exc, "code", "validation_error"))
        status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)

        logger.warning("Validation Error")

        return format_response(
            success=False,
            message="Validation failed",
            code=code,
            data=None,
            errors=exc.detail,
            request=request,
            status_code=status_code,
        )

    from rest_framework.views import exception_handler as drf_exception_handler

    response = drf_exception_handler(exc, context)

    if response is None:
        logger.exception("Unknown exception")

        return format_response(
            success=False,
            message="Internal server error",
            code="internal_server_error",
            data=None,
            errors=None,
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return format_response(
        success=False,
        message="Request failed",
        code=getattr(exc, "default_code", "error")
        if isinstance(exc, APIException)
        else "error",
        data=None,
        errors=response.data,
        request=request,
        status_code=response.status_code,
        headers=response.headers,
    )
