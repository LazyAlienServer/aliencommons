from django.utils import timezone
from django.contrib.auth import get_user_model

import user_agents

from ..models import UserSession
from logs.logging import get_logger

logger = get_logger(__name__)
User = get_user_model()


def create_user_session(request, user: User):
    """
    Create a new UserSession object at login.
    """
    session_key = request.session.session_key

    ip = request.META.get("REMOTE_ADDR")

    user_agent_raw = request.META.get("HTTP_USER_AGENT")
    if user_agent_raw is None:
        user_agent = None
        browser = None
        os = None
        device = None
    else:
        ua = user_agents.parse(user_agent_raw)
        user_agent = str(ua)
        browser = ua.browser.family
        os = ua.os.family
        device = ua.device.family

    user_session = UserSession.objects.create(
        user=user, session_key=session_key, user_agent=str(user_agent),
        browser=browser, os=os, device=device,
        ip_address=ip, last_accessed_at=timezone.now().date()
    )

    logger.info(
        f"Created new UserSession object {user_session.id} for user {user.username}"
    )


def delete_user_session(request):
    """
    Delete a user session at logout, or when user manually revoke a session.
    """
    user = request.user
    session_key = request.session.session_key
    user_session = UserSession.objects.filter(session_key=session_key).first()

    if user_session:
        user_session_id = user_session.id
        user_session.delete()
        extra = {}
        if user is not None:
            extra["user_id"] = user.id

        logger.info(
            f"Deleted UserSession {user_session_id} for session {session_key}",
            extra=extra
        )
    else:
        extra = {}
        if user is not None:
            extra["user_id"] = user.id

        logger.warning(
            f"(Found at logout) UserSession does not exist for session {session_key}",
            extra=extra
        )


def update_last_accessed_at(request):
    """
    Update `last_accessed_at` field of UserSession.
    """
    today = timezone.now().date()
    session_key = request.session.session_key
    UserSession.objects.filter(
        session_key=session_key
    ).exclude(
        last_accessed_at=today
    ).update(last_accessed_at=today)
