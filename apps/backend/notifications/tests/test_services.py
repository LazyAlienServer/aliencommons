from comments.services import create_comment
from core.tests.factories import (
    create_comment as create_comment_record,
    create_community_post,
    create_article_publication,
    create_article,
    create_user,
)
from core.tests.testcases import BaseTestCase
from notifications.models import NotificationEvent
from notifications.services import (
    fan_out_event,
    fan_out_pending_events,
    notify_subscribed_author_posted,
)
from users.models import UserSubscription


class NotificationServiceTests(BaseTestCase):
    def setUp(self):
        self.author = create_user(username="author")
        self.reader = create_user(username="reader")
        self.article = create_article(author=self.author, title="Guide")
        self.published = create_article_publication(self.article, title=self.article.source.title)

    def test_comment_mentions_and_reply_create_outbox_events(self):
        parent = create_comment_record(self.reader, self.published, body="Top")

        comment = create_comment(
            author=self.author,
            body="Hi {{mention:0}}",
            mentions=[str(self.reader.id)],
            target=parent.content_target,
        )

        self.assertEqual(comment.parent, parent)
        self.assertEqual(
            set(NotificationEvent.objects.values_list("reason", flat=True)),
            {
                NotificationEvent.Reason.MENTION,
                NotificationEvent.Reason.REPLY,
            },
        )
        self.assertEqual(
            set(NotificationEvent.objects.values_list("channel", flat=True)),
            {
                NotificationEvent.Channel.MENTIONS,
                NotificationEvent.Channel.REPLIES,
            },
        )

    def test_subscribed_author_event_fans_out_to_subscribers(self):
        UserSubscription.objects.create(subscriber=self.reader, subscribed_to=self.author)
        own_subscription = create_user(username="own")
        UserSubscription.objects.create(subscriber=own_subscription, subscribed_to=self.author)
        post = create_community_post(author=self.author, body="Post")
        event = notify_subscribed_author_posted(
            actor=self.author,
            target=post.content_target,
            content_kind="community_post-extra",
        )
        UserSubscription.objects.filter(subscriber=self.reader, subscribed_to=self.author).delete()

        result = fan_out_event(event_id=event.id)

        self.assertEqual(result["status"], "delivered")
        self.assertEqual(event.reason, NotificationEvent.Reason.SUBSCRIPTION)
        self.assertEqual(event.channel, NotificationEvent.Channel.SUBSCRIPTIONS)
        self.assertEqual(event.payload, {"content_kind": "community_post-extra"})
        self.assertEqual(
            set(event.deliveries.values_list("recipient_id", flat=True)),
            {self.reader.id, own_subscription.id},
        )

    def test_outbox_drain_retries_pending_events(self):
        UserSubscription.objects.create(subscriber=self.reader, subscribed_to=self.author)
        event = notify_subscribed_author_posted(
            actor=self.author,
            target=self.published.content_target,
            content_kind="article-publication-extra",
        )

        result = fan_out_pending_events()

        event.refresh_from_db()
        self.assertEqual(result, {"scanned": 1, "delivered": 1, "failed": 0})
        self.assertEqual(event.delivery_status, NotificationEvent.DeliveryStatus.DELIVERED)
        self.assertTrue(event.deliveries.filter(recipient=self.reader).exists())
