from types import SimpleNamespace

from rest_framework import status

from core.tests.testcases import BaseTestCase
from drf_std_response import format_response


class FormatResponseTests(BaseTestCase):
    def test_format_response_builds_standard_success_payload(self):
        request = SimpleNamespace(request_id="req-1", timestamp="2026-03-17T10:00:00Z")

        response = format_response(
            success=True,
            message="created",
            code="created",
            data={"id": 1},
            errors=None,
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "success": True,
                "message": "created",
                "code": "created",
                "data": {"id": 1},
                "errors": None,
                "meta": {
                    "request_id": "req-1",
                    "timestamp": "2026-03-17T10:00:00Z",
                },
            },
        )

    def test_format_response_defaults_meta_fields_when_request_missing(self):
        response = format_response(
            success=True,
            message="ok",
            code="ok",
            data={"ok": True},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["request_id"], None)
        self.assertEqual(response.data["meta"]["timestamp"], None)
