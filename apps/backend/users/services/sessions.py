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

    ip = request.META.get('REMOTE_ADDR', None)
    if ip is None:
        ip = "UNKNOWN"

    user_agent_raw = request.META.get('HTTP_USER_AGENT', None)
    if user_agent_raw is None:
        user_agent = "UNKNOWN"
        browser = "UNKNOWN"
        os = "UNKNOWN"
        device = "UNKNOWN"
    else:
        user_agent = user_agents.parse(user_agent_raw)
        browser = user_agent.browser.family
        os = user_agent.os.family
        device = user_agent.device.family

    user_session = UserSession.objects.create(
        user=user, session_key=session_key, user_agent=str(user_agent),
        broswer=browser, os=os, device=device,
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
    user_session = UserSession.objects.get(session_key=session_key)

    if user_session:
        user_session_id = user_session.id
        user_session.delete()
        logger.info(
            f"Deleted UserSession {user_session_id} for session {session_key}",
            extra={"user_id": user.id}
        )
    else:
        logger.warning(
            f"(Found at logout) UserSession does not exist for session {session_key}",
            extra={"user_id": user.id}
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
