from django.conf import settings

import requests

from .cache import set_cache


YOUTUBE_API_URL = settings.YOUTUBE_API_URL
YOUTUBE_REQUEST_HEADERS = settings.YOUTUBE_REQUEST_HEADERS


def fetch_youtube_data():
    """
    Fetch YouTube Data and Update Cache
    """
    namespace = 'youtube_data'
    entity = 'channel_stats'
    identifier = settings.YOUTUBE_CHANNEL_ID

    header, url = YOUTUBE_REQUEST_HEADERS, YOUTUBE_API_URL
    response = requests.get(url, headers=header)
    data = response.json()

    set_cache(
        namespace=namespace, entity=entity, identifier=identifier,
        value=data, timeout=None
    )
