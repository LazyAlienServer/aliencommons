from django.tasks import task


@task
def fan_out_notification_event_task(*, event_id):
    from .services import fan_out_event

    return fan_out_event(event_id=event_id)


@task
def fan_out_pending_notification_events_task(*, batch_size=100):
    from .services import fan_out_pending_events

    return fan_out_pending_events(batch_size=batch_size)
