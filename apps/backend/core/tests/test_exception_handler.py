from types import SimpleNamespace

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, ValidationError

from core.tests.testcases import BaseTestCase
from drf_std_response import ServiceError
from drf_std_response.exception_handlers import exception_handler


class CustomExceptionHandlerTests(BaseTestCase):
    def setUp(self):
        self.request = SimpleNamespace(request_id="req-1", timestamp="2026-03-17T10:00:00Z")
        self.context = {"request": self.request}

    def test_service_error_is_wrapped_with_standard_payload(self):
        response = exception_handler(
            ServiceError(detail="Bad state", code="bad_state"),
            self.context,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Bad state")
        self.assertEqual(response.data["code"], "bad_state")
        self.assertEqual(
            response.data["errors"],
            [{"code": "bad_state", "message": "Bad state", "field": None}],
        )
        self.assertEqual(response.data["meta"]["request_id"], "req-1")

    def test_validation_error_is_wrapped_with_validation_payload(self):
        response = exception_handler(
            ValidationError({"title": ["required"]}),
            self.context,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Validation failed")
        self.assertEqual(response.data["code"], "validation_error")
        self.assertEqual(
            response.data["errors"],
            [{"code": "invalid", "message": "required", "field": "title"}],
        )

    def test_nested_validation_errors_are_flattened_with_field_paths(self):
        response = exception_handler(
            ValidationError(
                {
                    "shipping_address": {
                        "non_field_errors": ["Unsupported address"],
                    },
                    "recipients": [
                        {"name": ["This field is required."]},
                        {"email": ["Enter a valid email address."]},
                    ],
                }
            ),
            self.context,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["errors"],
            [
                {
                    "code": "invalid",
                    "message": "Unsupported address",
                    "field": "shipping_address.non_field_errors",
                },
                {
                    "code": "invalid",
                    "message": "This field is required.",
                    "field": "recipients.0.name",
                },
                {
                    "code": "invalid",
                    "message": "Enter a valid email address.",
                    "field": "recipients.1.email",
                },
            ],
        )

    def test_builtin_api_exception_is_wrapped(self):
        response = exception_handler(NotAuthenticated(), self.context)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Request failed")
        self.assertEqual(response.data["code"], "not_authenticated")
        self.assertEqual(response.data["errors"][0]["field"], None)

    def test_django_permission_denied_is_wrapped(self):
        response = exception_handler(PermissionDenied(), self.context)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["code"], "permission_denied")

    def test_unknown_error_becomes_internal_server_error(self):
        response = exception_handler(RuntimeError("boom"), self.context)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Internal server error")
        self.assertEqual(response.data["code"], "internal_server_error")
        self.assertEqual(response.data["errors"][0]["field"], None)

    def test_http404_is_wrapped(self):
        response = exception_handler(Http404(), self.context)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["code"], "not_found")
