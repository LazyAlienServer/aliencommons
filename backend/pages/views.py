from django.conf import settings

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from datetime import datetime

from core.utils.cache import get_cache


def days_since_start(date="2023-03-17"):
    now = datetime.now()
    delta = now - datetime.strptime(date, "%Y-%m-%d")
    return delta.days


def _fetch_youtube_cache():
    """
    Fetch cached YouTube data
    """
    namespace = 'youtube_data'
    entity = 'channel_stats'
    identifier = settings.YOUTUBE_CHANNEL_ID

    raw_data = get_cache(
        namespace=namespace, entity=entity, identifier=identifier
    )

    if not raw_data:
        return None

    items = raw_data.get("items") or []
    if not items:
        return None
    
    data = items[0]

    return data


class YoutubeSnapshotView(APIView):
    """
    Return YouTube Channel Snapshot
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        data = _fetch_youtube_cache()

        if data:
            thumbnail_url = data["snippet"]["thumbnails"]["high"]["url"]
            subscriber_count = data["statistics"]["subscriberCount"]
            video_count = data["statistics"]["videoCount"]
            view_count = data["statistics"]["viewCount"]

            return Response({
                "thumbnail_url": thumbnail_url,
                "subscriber_count": subscriber_count,
                "video_count": video_count,
                "view_count": view_count,
                "since": days_since_start(),
            })
        else:
            return Response({"error": "No data found in cache"})
