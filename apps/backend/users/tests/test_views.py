from unittest.mock import patch

from django.conf import settings
from django.urls import reverse

from rest_framework import status

from core.tests.factories import create_user
from core.tests.testcases import BaseAPITestCase
from core.utils.cache import set_cache
from users.models import EmailAddress, User, UserSession
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
            status_code=status.HTTP_403_FORBIDDEN,
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


class SessionViewTests(BaseAPITestCase):
    def setUp(self):
        self.user = create_user(username="captain", password="secret123")
        self.email_address = EmailAddress.objects.create(
            user=self.user,
            email="captain@example.com",
            is_primary=True,
            is_verified=True,
        )

    def test_login_creates_user_session_and_persists_auth_session(self):
        response = self.post_json(
            reverse("session-login"),
            {
                "email": self.email_address.email,
                "password": "secret123",
            },
            HTTP_USER_AGENT=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/135.0.0.0 Safari/537.36"
            ),
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="user_login",
            message="user login successfully",
        )

        session = self.client.session
        self.assertEqual(str(session["_auth_user_id"]), str(self.user.id))
        self.assertIn(settings.SESSION_EXPIRY_REFRESH_FIELD, session)

        user_session = UserSession.objects.get(user=self.user)
        self.assertEqual(user_session.session_key, session.session_key)
        self.assertEqual(user_session.browser, "Chrome")
        self.assertEqual(user_session.os, "Mac OS X")
        self.assertEqual(user_session.last_accessed_at, response.wsgi_request.timestamp.date())

    def test_login_rejects_unverified_email(self):
        self.email_address.is_verified = False
        self.email_address.save(update_fields=["is_verified"])

        response = self.post_json(
            reverse("session-login"),
            {
                "email": self.email_address.email,
                "password": "secret123",
            },
        )

        self.assert_error_response(
            response,
            status_code=status.HTTP_403_FORBIDDEN,
            code="authentication_failed",
            message="Request failed",
        )
        self.assertFalse(UserSession.objects.exists())

    def test_logout_deletes_user_session_and_clears_authentication(self):
        self.post_json(
            reverse("session-login"),
            {
                "email": self.email_address.email,
                "password": "secret123",
            },
        )
        self.assertEqual(UserSession.objects.count(), 1)

        response = self.post_json(reverse("session-logout"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="user_logout",
            message="user logout successfully",
        )
        self.assertEqual(UserSession.objects.count(), 0)

        me_response = self.get_json(reverse("profile-me"))
        self.assert_error_response(
            me_response,
            status_code=status.HTTP_403_FORBIDDEN,
            code="not_authenticated",
            message="Request failed",
        )
