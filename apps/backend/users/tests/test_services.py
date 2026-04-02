from unittest.mock import patch

from django.conf import settings

from core.exceptions import ServiceError
from core.tests.factories import create_user
from core.tests.testcases import BaseTestCase
from core.utils.cache import get_cache, set_cache
from users.models import EmailAddress
from users.services.users import _hash_code, register, verify_email


class UserServiceTests(BaseTestCase):
    def setUp(self):
        self.email = "captain@example.com"
        self.user = create_user(username="captain")
        self.email_address = EmailAddress.objects.create(
            user=self.user,
            email=self.email,
            is_verified=False,
            is_primary=True,
        )

    @patch("users.services.users.send_verification_email_task")
    @patch("users.services.users._generate_6_digit_code", return_value="123456")
    @patch("users.services.users.random.choice", return_value="default_avatar/Axe.webp")
    def test_register_creates_user_email_and_verification_state(
        self,
        random_choice_mock,
        generate_code_mock,
        send_task_mock,
    ):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            result = register(
                username="new-user",
                email="new-user@example.com",
                password="secret123",
            )

        user = EmailAddress.objects.select_related("user").get(email="new-user@example.com").user
        stored_hash = get_cache(
            namespace="email_verification",
            entity="code",
            identifier="new-user@example.com",
        )

        self.assertEqual(result["user_id"], user.id)
        self.assertEqual(result["username"], "new-user")
        self.assertEqual(result["email"], "new-user@example.com")
        self.assertFalse(result["email_verified"])
        self.assertEqual(result["resend_cooldown_seconds"], settings.VERIFICATION_CODE_RESEND_COOLDOWN)
        self.assertEqual(result["code_ttl_seconds"], settings.VERIFICATION_CODE_TTL)
        self.assertEqual(user.avatar.name, "default_avatar/Axe.webp")
        self.assertEqual(
            stored_hash,
            _hash_code("new-user@example.com", "123456"),
        )
        random_choice_mock.assert_called_once()
        generate_code_mock.assert_called_once()
        self.assertEqual(len(callbacks), 1)
        send_task_mock.enqueue.assert_called_once_with(
            to_email="new-user@example.com",
            code="123456",
        )

    def test_verify_email_marks_email_and_user_as_verified(self):
        set_cache(
            namespace="email_verification",
            entity="code",
            identifier=self.email,
            value=_hash_code(self.email, "123456"),
            timeout=settings.VERIFICATION_CODE_TTL,
        )

        result = verify_email(user=self.user, email=self.email, code="123456")

        self.email_address.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(result, {"email": self.email})
        self.assertTrue(self.email_address.is_verified)
        self.assertTrue(self.user.is_email_verified)
        self.assertEqual(
            get_cache(namespace="email_verification", entity="code", identifier=self.email),
            None,
        )

    def test_verify_email_raises_when_code_missing(self):
        with self.assertRaises(ServiceError) as exc:
            verify_email(user=self.user, email=self.email, code="123456")

        self.assertEqual(exc.exception.code, "code_not_found")

    def test_verify_email_increments_attempts_on_wrong_code(self):
        set_cache(
            namespace="email_verification",
            entity="code",
            identifier=self.email,
            value=_hash_code(self.email, "123456"),
            timeout=settings.VERIFICATION_CODE_TTL,
        )

        with self.assertRaises(ServiceError) as exc:
            verify_email(user=self.user, email=self.email, code="654321")

        self.assertEqual(exc.exception.code, "incorrect_code")
        self.assertEqual(
            get_cache(namespace="email_verification", entity="attempts", identifier=self.email),
            1,
        )

    def test_verify_email_raises_when_max_attempts_reached(self):
        set_cache(
            namespace="email_verification",
            entity="code",
            identifier=self.email,
            value=_hash_code(self.email, "123456"),
            timeout=settings.VERIFICATION_CODE_TTL,
        )
        set_cache(
            namespace="email_verification",
            entity="attempts",
            identifier=self.email,
            value=settings.MAX_VERIFICATION_ATTEMPTS - 1,
            timeout=settings.VERIFICATION_CODE_TTL,
        )

        with self.assertRaises(ServiceError) as exc:
            verify_email(user=self.user, email=self.email, code="654321")

        self.assertEqual(exc.exception.code, "max_attempts_reached")

    def test_verify_email_raises_when_email_address_not_found(self):
        stranger = create_user(username="stranger")

        with self.assertRaises(ServiceError) as exc:
            verify_email(user=stranger, email="missing@example.com", code="123456")

        self.assertEqual(exc.exception.code, "email_address_not_found")
