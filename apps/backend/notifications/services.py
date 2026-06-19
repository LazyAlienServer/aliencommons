from django.db import transaction
from django.utils import timezone

from users.models import UserSubscription

from .models import NotificationDelivery, NotificationEvent
from .tasks import fan_out_notification_event_task


def _queue_fan_out(event):
    transaction.on_commit(
        lambda: fan_out_notification_event_task.enqueue(event_id=str(event.id))
    )


def create_event(*, reason, actor, target, payload=None, recipients=None, dedupe_key):
    event, created = NotificationEvent.objects.get_or_create(
        dedupe_key=dedupe_key,
        defaults={
            "reason": reason,
            "actor": actor,
            "target": target,
            "payload": payload or {},
            "recipients": recipients or [],
        },
    )
    if created:
        _queue_fan_out(event)
    return event


def notify_mentions(*, actor, target, mention_user_ids, dedupe_prefix):
    recipient_ids = sorted({str(user_id) for user_id in mention_user_ids if str(user_id) != str(actor.id)})
    if not recipient_ids:
        return None
    return create_event(
        reason=NotificationEvent.Reason.MENTION,
        actor=actor,
        target=target,
        recipients=recipient_ids,
        dedupe_key=f"mention:{dedupe_prefix}:{','.join(recipient_ids)}",
    )


def notify_comment_reply(*, comment):
    replied_to = comment.target.comment
    if replied_to.author_id is None or replied_to.author_id == comment.author_id:
        return None
    return create_event(
        reason=NotificationEvent.Reason.REPLY,
        actor=comment.author,
        target=comment.content_target,
        recipients=[str(replied_to.author_id)],
        dedupe_key=f"comment-reply:{comment.id}:{replied_to.id}",
    )


def notify_subscribed_author_posted(*, actor, target, content_kind):
    recipient_ids = sorted(
        str(subscriber_id)
        for subscriber_id in UserSubscription.objects.filter(
            subscribed_to_id=actor.id,
        ).values_list("subscriber_id", flat=True)
        if str(subscriber_id) != str(actor.id)
    )
    if not recipient_ids:
        return None
    return create_event(
        reason=NotificationEvent.Reason.SUBSCRIPTION,
        actor=actor,
        target=target,
        payload={"content_kind": content_kind},
        recipients=recipient_ids,
        dedupe_key=f"subscribed-author-posted:{content_kind}:{target.id}",
    )


def _recipient_ids(event):
    return event.recipients


def fan_out_event(*, event_id):
    with transaction.atomic():
        event = NotificationEvent.objects.select_for_update().get(id=event_id)
        if event.delivery_status == NotificationEvent.DeliveryStatus.DELIVERED:
            return {"created": 0, "status": "already_delivered"}
        event.delivery_status = NotificationEvent.DeliveryStatus.PROCESSING
        event.delivery_attempts += 1
        event.last_error = ""
        event.save(update_fields=["delivery_status", "delivery_attempts", "last_error", "updated_at"])

    try:
        recipient_ids = {
            str(recipient_id)
            for recipient_id in _recipient_ids(event)
            if str(recipient_id) != str(event.actor_id)
        }
        deliveries = [
            NotificationDelivery(event=event, recipient_id=recipient_id)
            for recipient_id in recipient_ids
        ]
        created = NotificationDelivery.objects.bulk_create(deliveries, ignore_conflicts=True)
    except Exception as exc:
        event.delivery_status = NotificationEvent.DeliveryStatus.FAILED
        event.last_error = str(exc)
        event.save(update_fields=["delivery_status", "last_error", "updated_at"])
        raise

    event.delivery_status = NotificationEvent.DeliveryStatus.DELIVERED
    event.delivered_at = timezone.now()
    event.save(update_fields=["delivery_status", "delivered_at", "updated_at"])
    return {"created": len(created), "status": "delivered"}


def fan_out_pending_events(*, batch_size=100):
    event_ids = list(
        NotificationEvent.objects.filter(
            delivery_status__in=[
                NotificationEvent.DeliveryStatus.PENDING,
                NotificationEvent.DeliveryStatus.PROCESSING,
                NotificationEvent.DeliveryStatus.FAILED,
            ],
        )
        .order_by("created_at")
        .values_list("id", flat=True)[:batch_size]
    )
    delivered = 0
    failed = 0
    for event_id in event_ids:
        try:
            fan_out_event(event_id=event_id)
            delivered += 1
        except Exception:
            failed += 1
    return {"scanned": len(event_ids), "delivered": delivered, "failed": failed}


def mark_delivery_read(delivery):
    if delivery.read_at is None:
        delivery.read_at = timezone.now()
        delivery.save(update_fields=["read_at", "updated_at"])
    return delivery


def mark_all_deliveries_read(*, recipient):
    return NotificationDelivery.objects.filter(
        recipient=recipient,
        read_at__isnull=True,
    ).update(read_at=timezone.now())
