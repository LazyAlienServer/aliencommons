from django.urls import reverse
from rest_framework import status

from core.tests.factories import create_user
from core.tests.testcases import BaseAPITestCase
from notifications.models import NotificationDelivery, NotificationEvent


class NotificationViewTests(BaseAPITestCase):
    def setUp(self):
        self.recipient = create_user(username="recipient")
        self.other_user = create_user(username="other")
        self.event = NotificationEvent.objects.create(
            event_type=NotificationEvent.EventType.NEW_SUBSCRIBER,
            actor=self.other_user,
            data={"recipient_ids": [str(self.recipient.id)]},
            dedupe_key="view-event",
        )
        self.delivery = NotificationDelivery.objects.create(
            event=self.event,
            recipient=self.recipient,
        )

    def test_user_lists_only_own_notifications(self):
        NotificationDelivery.objects.create(event=self.event, recipient=self.other_user)
        self.authenticate(self.recipient)

        response = self.get_json(reverse("notification-list"))

        self.assert_success_response(response, status_code=status.HTTP_200_OK, code="listed")
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["event_type"], self.event.event_type)

    def test_user_can_mark_one_and_all_notifications_read(self):
        second_event = NotificationEvent.objects.create(
            event_type=NotificationEvent.EventType.MENTION,
            actor=self.other_user,
            data={"recipient_ids": [str(self.recipient.id)]},
            dedupe_key="second-view-event",
        )
        second_delivery = NotificationDelivery.objects.create(
            event=second_event,
            recipient=self.recipient,
        )
        self.authenticate(self.recipient)

        unread = self.get_json(reverse("notification-unread-count"))
        marked = self.post_json(reverse("notification-mark-read", args=[self.delivery.id]))
        marked_all = self.post_json(reverse("notification-mark-all-read"))

        second_delivery.refresh_from_db()
        self.assertEqual(unread.data["data"]["count"], 2)
        self.assert_success_response(marked, status_code=status.HTTP_200_OK, code="marked_read")
        self.assert_success_response(marked_all, status_code=status.HTTP_200_OK, code="marked_all_read")
        self.assertIsNotNone(second_delivery.read_at)
