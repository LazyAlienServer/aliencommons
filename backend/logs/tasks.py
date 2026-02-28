from celery import shared_task
from django.utils import timezone

from datetime import timedelta

from .models import FrontendLog


def delete_old_logs(level, days):
    cutoff = timezone.now() - timedelta(days=days)

    logs_deleted, _ = FrontendLog.objects.filter(
        level__in=[level],
        timestamp__lt=cutoff
    ).delete()

    # Return the number of debug logs
    return logs_deleted


@shared_task
def clear_debug_logs(days=14):
    debug_deleted = delete_old_logs('info', days)
    return {"status": "success", "message": f"{debug_deleted} old debug logs cleared"}


@shared_task
def clear_info_logs(days=30):
    info_deleted = delete_old_logs('info', days)
    return {"status": "success", "message": f"{info_deleted} old info logs cleared"}


@shared_task
def clear_warn_logs(days=90):
    warn_deleted = delete_old_logs('warn', days)
    return {"status": "success", "message": f"{warn_deleted} old warn logs cleared"}
