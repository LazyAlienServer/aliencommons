from unittest.mock import patch

from django.conf import settings
from django.urls import reverse

from rest_framework import status

from core.tests.factories import create_user
from core.tests.testcases import BaseAPITestCase
from core.utils.cache import set_cache
from users.models import EmailAddress, User
from users.services.users import _hash_code


class UserViewTests(BaseAPITestCase):
    def setUp(self):
        self.user = create_user(username="captain")
        self.email_address = EmailAddress.objects.create(
            user=self.user,
            email="captain@example.com",
            is_primary=True,
            is_verified=False,
        )
        self.other_user = create_user(username="navigator")

    @patch("users.services.users.send_verification_email_task")
    @patch("users.services.users._generate_6_digit_code", return_value="123456")
    @patch("users.services.users.random.choice", return_value="default_avatar/Axe.webp")
    def test_register_endpoint_returns_standard_success_response(
        self,
        random_choice_mock,
        generate_code_mock,
        send_task_mock,
    ):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.post_json(
                reverse("profile-list"),
                {
                    "username": "new-user",
                    "email": "new-user@example.com",
                    "password": "secret123",
                    "confirm_password": "secret123",
                },
            )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="user_registered",
            message="user registered successfully",
        )
        self.assertEqual(response.data["data"]["username"], "new-user")
        self.assertEqual(response.data["data"]["email"], "new-user@example.com")
        self.assertEqual(User.objects.filter(username="new-user").count(), 1)
        self.assertEqual(len(callbacks), 1)
        send_task_mock.enqueue.assert_called_once()
        random_choice_mock.assert_called_once()
        generate_code_mock.assert_called_once()

    def test_profile_list_returns_paginated_standard_response(self):
        response = self.get_json(reverse("profile-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
            message="listed",
        )
        self.assertEqual(response.data["data"]["count"], 2)
        self.assertEqual(len(response.data["data"]["results"]), 2)

    def test_retrieve_profile_returns_standard_response(self):
        response = self.get_json(reverse("profile-detail", args=[self.user.id]))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="retrieved",
            message="retrieved",
        )
        self.assert_uuid_equal(response.data["data"]["id"], self.user.id)
        self.assertEqual(response.data["data"]["username"], "captain")

    def test_me_requires_authentication(self):
        response = self.get_json(reverse("profile-me"))

        self.assert_error_response(
            response,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="not_authenticated",
            message="Request failed",
        )

    def test_me_returns_current_user_profile(self):
        self.authenticate(self.user)

        response = self.get_json(reverse("profile-me"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="my_profile_retrieved",
            message="my profile retrieved",
        )
        self.assert_uuid_equal(response.data["data"]["id"], self.user.id)
        self.assertEqual(response.data["data"]["username"], "captain")

    def test_me_patch_updates_username(self):
        self.authenticate(self.user)

        response = self.patch_json(
            reverse("profile-me"),
            {"username": "captain-renamed"},
        )

        self.user.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="my_profile_updated",
            message="my profile updated",
        )
        self.assertEqual(self.user.username, "captain-renamed")

    def test_verify_email_endpoint_marks_email_as_verified(self):
        set_cache(
            namespace="email_verification",
            entity="code",
            identifier=self.email_address.email,
            value=_hash_code(self.email_address.email, "123456"),
            timeout=settings.VERIFICATION_CODE_TTL,
        )
        self.authenticate(self.user)

        response = self.post_json(
            reverse("email-verify-email"),
            {"email": self.email_address.email, "code": "123456"},
        )

        self.email_address.refresh_from_db()
        self.user.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="email_verified",
            message="email verified successfully",
        )
        self.assertEqual(response.data["data"]["email"], self.email_address.email)
        self.assertTrue(self.email_address.is_verified)
        self.assertTrue(self.user.is_email_verified)
