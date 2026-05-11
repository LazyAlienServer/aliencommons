from django.contrib.contenttypes.models import ContentType
from django.db import transaction


from .models import Notification


@transaction.atomic
def create_notification(
    *,
    recipient,
    actor,
    notification_type,
    verb,
    dedupe_key,
    data=None,
    target=None,
    action_object=None,
):
    actor_content_type = ContentType.objects.get_for_model(actor)
    
    defaults = {
        "recipient": recipient,
        "actor_content_type": actor_content_type,
        "actor_object_id": actor.id,
        "notification_type": notification_type,
        "verb": verb,
        "data": data or {},
    }
    
    if target is not None:
        target_content_type = ContentType.objects.get_for_model(target)
        defaults["target_content_type"] = target_content_type
        defaults["target_object_id"] = target.id
    
    if action_object is not None:
        action_object_content_type = ContentType.objects.get_for_model(action_object)
        defaults["action_object_content_type"] = action_object_content_type
        defaults["action_object_object_id"] = action_object.id
    
    return Notification.objects.get_or_create(
        dedupe_key=dedupe_key,
        defaults=defaults,
    )


def create_mention_notifications_for_comment(comment, previous_mentions=None):
    mention_ids = set(comment.mentions or [])
    
    if previous_mentions is not None:
        previous_ids = set(previous_mentions)
        mention_ids = mention_ids - previous_ids
    
    mention_ids.discard(str(comment.author_id))
    
    notifications = []
    for user_id in mention_ids:
        from users.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            continue
        
        dedupe_key = f"comment:{comment.id}:mention:{user_id}"
        data = {
            "comment_id": str(comment.id),
            "author_id": str(comment.author_id),
            "author_username": comment.author.username,
        }
        
        notification, created = create_notification(
            recipient=user,
            actor=comment.author,
            action_object=comment,
            target=comment.target if hasattr(comment, 'target') else None,
            notification_type="mention",
            verb="mentioned you in a comment",
            dedupe_key=dedupe_key,
            data=data,
        )
        
        if created:
            notifications.append(notification)
    
    return notifications


def mark_notification_read(notification):
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read"])
    return notification


def mark_all_notifications_read(user):
    return Notification.objects.filter(
        recipient=user,
        is_read=False,
    ).update(is_read=True)


def get_unread_count(user):
    return Notification.objects.filter(
        recipient=user,
        is_read=False,
    ).count()
