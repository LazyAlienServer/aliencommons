from django.db import IntegrityError, transaction

from core.tests.factories import create_user
from core.tests.testcases import BaseTestCase
from users.models import EmailAddress, User, UserSubscription


class UserModelTests(BaseTestCase):
    def test_create_user_trims_username_and_hashes_password(self):
        user = User.objects.create_user(username="  alice  ", password="secret123")

        self.assertEqual(user.username, "alice")
        self.assertTrue(user.check_password("secret123"))

    def test_create_user_requires_username(self):
        with self.assertRaises(ValueError) as exc:
            User.objects.create_user(username="", password="secret123")

        self.assertEqual(str(exc.exception), "Username field must be filled")

    def test_create_user_requires_password(self):
        with self.assertRaises(ValueError) as exc:
            User.objects.create_user(username="alice", password="")

        self.assertEqual(str(exc.exception), "Password must be set")

    def test_create_superuser_sets_required_flags(self):
        user = User.objects.create_superuser(
            username="admin",
            password="secret123",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertFalse(EmailAddress.objects.filter(user=user).exists())

    def test_create_superuser_requires_staff_flag(self):
        with self.assertRaises(ValueError) as exc:
            User.objects.create_superuser(
                username="admin",
                password="secret123",
                is_staff=False,
            )

        self.assertEqual(str(exc.exception), "Superuser must have 'is_staff=True'.")

    def test_user_string_representation_is_username(self):
        user = create_user(username="captain")

        self.assertEqual(str(user), "captain")

    def test_email_address_string_representation_is_email(self):
        user = create_user()
        email_address = EmailAddress.objects.create(
            user=user,
            email="captain@example.com",
            is_primary=True,
        )

        self.assertEqual(str(email_address), "captain@example.com")

    def test_email_address_allows_only_one_primary_email_per_user(self):
        user = create_user()
        EmailAddress.objects.create(
            user=user,
            email="first@example.com",
            is_primary=True,
        )

        with self.assertRaises(IntegrityError):
            EmailAddress.objects.create(
                user=user,
                email="second@example.com",
                is_primary=True,
            )

    def test_user_subscription_string_representation(self):
        subscriber = create_user(username="reader")
        author = create_user(username="author")
        subscription = UserSubscription.objects.create(
            subscriber=subscriber,
            subscribed_to=author,
        )

        self.assertEqual(str(subscription), "reader subscribes to author")

    def test_user_subscription_rejects_duplicates(self):
        subscriber = create_user(username="reader")
        author = create_user(username="author")
        UserSubscription.objects.create(subscriber=subscriber, subscribed_to=author)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserSubscription.objects.create(subscriber=subscriber, subscribed_to=author)

    def test_user_subscription_rejects_self_subscription(self):
        user = create_user(username="reader")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserSubscription.objects.create(subscriber=user, subscribed_to=user)
