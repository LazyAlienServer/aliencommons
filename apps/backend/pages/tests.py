from unittest.mock import patch

from django.conf import settings
from django.urls import reverse

from rest_framework import status

from core.tests.testcases import BaseAPITestCase
from core.utils.cache import set_cache


class YoutubeSnapshotViewTests(BaseAPITestCase):
    def setUp(self):
        self.url = reverse("youtube_channel_snapshot")

    @patch("pages.views.days_since_start", return_value=42)
    def test_returns_cached_youtube_snapshot_in_standard_response(self, days_since_start_mock):
        set_cache(
            namespace="youtube_data",
            entity="channel_stats",
            identifier=settings.YOUTUBE_CHANNEL_ID,
            value={
                "items": [
                    {
                        "snippet": {
                            "thumbnails": {
                                "high": {"url": "https://example.com/thumb.jpg"},
                            }
                        },
                        "statistics": {
                            "subscriberCount": "1000",
                            "videoCount": "25",
                            "viewCount": "50000",
                        },
                    }
                ]
            },
        )

        response = self.get_json(self.url)

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="ok",
            message="ok",
        )
        self.assertEqual(
            response.data["data"],
            {
                "thumbnail_url": "https://example.com/thumb.jpg",
                "subscriber_count": "1000",
                "video_count": "25",
                "view_count": "50000",
                "since": 42,
            },
        )
        days_since_start_mock.assert_called_once()

    def test_returns_not_found_when_youtube_snapshot_is_missing(self):
        response = self.get_json(self.url)

        self.assert_error_response(
            response,
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found",
            message="Request failed",
        )
