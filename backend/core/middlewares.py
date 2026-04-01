from django.utils import timezone

import uuid

from logs.logging.context import add_log_context, clear_log_context
from logs.logging.logger import get_logger

logger = get_logger(__name__)


class RequestMetaMiddleware:
    """
    Add Meta Information to the Request object.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4().hex)
        timestamp = timezone.now()

        request.request_id = request_id
        request.timestamp = timestamp

        response = self.get_response(request)

        return response


class RequestLoggingMiddleware:
    """
    Log at the beginning and end of each request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = timezone.now()

        request_id = getattr(request, 'request_id', None)
        if request_id:
            add_log_context(request_id=request_id)
        else:
            logger.warning("Request id does not exist")

        logger.info(f"Request started: {request.method} {request.path}")

        response = self.get_response(request)

        duration_ms = int((timezone.now() - started_at).total_seconds() * 1000)

        logger.info(
            f"Request completed: {request.method} {request.path} "
            f"status={request.status_code} duration_ms={duration_ms}"
        )

        clear_log_context()
        return response
