import requests
from django.conf import settings

from core.exceptions import ServiceError


def render_markdown_to_html(markdown: str) -> str:
    """
    Render Markdown by calling the internal alienmark service.
    """
    try:
        response = requests.post(
            f"{settings.ALIENMARK_SERVICE_URL}/render-html",
            json={"markdown": markdown},
            timeout=settings.ALIENMARK_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ServiceError(
            detail="Failed to render markdown.",
            code="alienmark_render_failed",
        ) from exc

    try:
        data = response.json()
        html = data["html"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ServiceError(
            detail="Invalid response from markdown renderer.",
            code="alienmark_invalid_response",
        ) from exc

    if not isinstance(html, str):
        raise ServiceError(
            detail="Invalid html returned from markdown renderer.",
            code="alienmark_invalid_response",
        )

    return html
