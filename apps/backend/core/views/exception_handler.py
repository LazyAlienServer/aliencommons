from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError

from core.responses import format_api_response
from core.exceptions import ServiceError
from logs.logging.logger import get_logger

logger = get_logger(__name__)


def custom_exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default, drf handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    request = context.get('request')

    # Service layer errors
    if isinstance(exc, ServiceError):
        message = str(getattr(exc, 'detail', "Request failed"))
        code = str(getattr(exc, 'code', 'request_failed'))
        status_code = getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)

        logger.warning(f"Service Error: {message}")

        return format_api_response(
            success=False, message=message, code=code,
            data=None, errors=None, request=request,
            status_code=status_code
        )

    # Serializer layer (validation) errors
    if isinstance(exc, ValidationError):
        code = str(getattr(exc, 'code', 'validation_error'))
        status_code = getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)

        logger.warning(f"Validation Error")

        return format_api_response(
            success=False, message="Validation failed", code=code,
            data=None, errors=exc.detail, request=request,
            status_code=status_code
        )

    # DRF/Django built-in errors: Http404, PermissionDenied, Subclasses of APIException other than ValidationError
    response = exception_handler(exc, context)

    # Unknown error
    if response is None:
        logger.exception("Unknown exception")

        return format_api_response(
            success=False, message="Internal server error", code='internal_server_error',
            data=None, errors=None, request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Wrap DRF exception_handler response into the standard format
    return format_api_response(
        success=False,
        message="Request failed",
        code=getattr(exc, "default_code", "error") if isinstance(exc, APIException) else "error",
        data=None,
        errors=response.data,
        request=request,
        status_code=response.status_code,
        headers=response.headers,
    )
