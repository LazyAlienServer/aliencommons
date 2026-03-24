from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.module_loading import import_string

import logging
from dataclasses import dataclass

from core.utils.cache import get_key, add_cache, delete_cache
from .models import PeriodicTask
from .utils import compute_next_enqueue_at

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class SchedulerRunResult:
    """
    Use this data class to build a standard scheduler run result.
    """
    scanned: int = 0
    enqueued: int = 0
    failed: int = 0


def acquire_scheduler_lock(*, identifier="dispatch", ttl=30):
    """
    Acquire a coarse lock so only one scheduler loop dispatches due jobs.

    With django-redis, ``cache.lock`` returns a proper distributed lock.
    In simpler backends we fall back to ``cache.add`` for a best-effort lock.

    PS: dispatch (分派/调度)
    """
    key = get_key(namespace='scheduler', entity='lock', identifier=identifier)
    lock_function = getattr(cache, "lock", None)

    if callable(lock_function):
        return lock_function(key, timeout=ttl)

    return _CacheAddLock(identifier=identifier, ttl=ttl)


def _lock_is_acquired(lock):
    if isinstance(lock, _CacheAddLock):
        return lock.acquired
    return True


def dispatch_task(*, task, now):
    """
    Enqueue one due schedule and advance its next run time.

    This method intentionally does not execute the task itself. It only
    dispatches to the task queue and updates scheduling metadata.
    """
    task_function = import_string(task.task)
    args = task.args
    kwargs = task.kwargs
    queue_name = task.queue_name or "default"

    with (transaction.atomic()):
        locked_task = PeriodicTask.objects.select_for_update().get(pk=task.pk)

        task_function.using(queue_name=queue_name).enqueue(*args, **kwargs)

        locked_task.last_enqueued_at = now

        locked_task.next_enqueue_at = compute_next_enqueue_at(
            interval_seconds=locked_task.interval.in_seconds
        )

        locked_task.save(update_fields=['last_enqueued_at', 'next_enqueue_at'])

    logger.info(
        "Scheduled task enqueued",
        extra={
            "task_id": str(locked_task.id),
            "task_name": locked_task.name,
            "task_path": locked_task.task,
            "queue_name": queue_name,
            "next_enqueue_at": locked_task.next_enqueue_at.isoformat() if locked_task.next_enqueue_at else None,
        },
    )


def enqueue_due_tasks(tasks):
    """
    The main entrance for scheduled tasks, should be called by a management command.
    Dispatch at most 'batch_size' due schedules.
    In other words, batch_size is the maximum number of schedules run in a single run.
    """
    now = timezone.now()
    batch_size = 100

    with acquire_scheduler_lock() as lock:

        # Prevent task to be run twice
        if not _lock_is_acquired(lock):
            logger.info("Scheduler dispatch skipped because another scheduler holds the lock")
            return SchedulerRunResult(scanned=0, enqueued=0, failed=0)

        due_tasks = list(
            tasks.filter(next_enqueue_at__lte=now).order_by("next_enqueue_at")[:batch_size]
        )

        enqueued = 0
        for task in due_tasks:
            dispatch_task(task=task, now=now)
            enqueued += 1

        scanned = len(due_tasks)
        failed = scanned - enqueued

        return SchedulerRunResult(scanned=scanned, enqueued=enqueued, failed=failed)


class _CacheAddLock:
    """
    Return a context manager that is similar to 'cache.lock'.

    Note that '__enter__' and '__exit__' methods are necessary for a context manager.
    """
    def __init__(self, *, identifier, ttl):
        self.identifier = identifier
        self.ttl = ttl
        self.acquired = False

    def __enter__(self):
        self.acquired = add_cache(
            namespace='scheduler', entity='lock', identifier=self.identifier,
            value="1", timeout=self.ttl
        )
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.acquired:
            delete_cache(
                namespace='scheduler', entity='lock', identifier=self.identifier,
            )
        return False
