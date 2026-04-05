from django.conf import settings
from django.utils import timezone

from datetime import datetime, timedelta

from logs.logging import get_logger
from .services.sessions import update_last_accessed_at

logger = get_logger(__name__)


class SessionTrackingMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not request.user.is_authenticated:
            return response

        session_key = request.session.session_key
        if session_key is None:
            return response

        update_last_accessed_at(request)

        now = timezone.now()
        should_refresh = False
        raw_last_refresh_at = request.session.get(settings.SESSION_EXPIRY_REFRESH_FIELD)
        if raw_last_refresh_at is None:
            should_refresh = True
            logger.warning(
                f"{settings.SESSION_EXPIRY_REFRESH_FIELD} doesn't exist in request.session",
                extra={
                    'session_key': session_key,
                }
            )
        else:
            last_refresh_at = datetime.fromisoformat(raw_last_refresh_at)
            interval = settings.SESSION_EXPIRY_REFRESH_INTERVAL

            if now - last_refresh_at >= timedelta(seconds=interval):
                should_refresh = True

        if should_refresh:
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            request.session[settings.SESSION_EXPIRY_REFRESH_FIELD] = now.isoformat()

        return response
