from django.tasks import task

from core.utils.youtube import fetch_youtube_data
from logs.logging import get_logger

logger = get_logger(__name__)


@task
def refresh_youtube_cache():
    try:
        fetch_youtube_data()
        logger.info("YouTube channel data successfully refreshed")
    except Exception:
        logger.exception("Failed to fetch YouTube channel data")
        raise
