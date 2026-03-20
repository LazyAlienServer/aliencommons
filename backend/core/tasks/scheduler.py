from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.module_loading import import_string

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from core.utils.cache import get_key, add_cache, delete_cache

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class SchedulerRunResult:
    """
    Use this data class to build a standard scheduler run result.
    """
    scanned: int = 0
    enqueued: int = 0
    skipped: int = 0


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


def compute_next_run_at(*, previous_run_at, interval_seconds) -> datetime:
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be greater than 0")
    return previous_run_at + timedelta(seconds=interval_seconds)


def dispatch_schedule(*, schedule, now=None):
    """
    Enqueue one due schedule and advance its next run time.

    This method intentionally does not execute the task itself. It only
    dispatches to the task queue and updates scheduling metadata.
    """
    now = now or timezone.now()

    if not schedule.is_enabled:
        return False

    task = import_string(schedule.task_path)
    args = schedule.args_json or []
    kwargs = schedule.kwargs_json or {}
    queue_name = schedule.queue_name or "default"

    with transaction.atomic():
        manager = getattr(type(schedule), "objects")
        locked_schedule = manager.select_for_update().get(pk=schedule.pk)

        # Re-check inside the transaction so concurrent scheduler loops do not
        # enqueue the same record twice.
        if not locked_schedule.is_enabled:
            return False

        if locked_schedule.next_run_at and locked_schedule.next_run_at > now:
            return False

        task.enqueue(
            *args,
            **kwargs,
            queue_name=queue_name,
        )

        locked_schedule.last_enqueued_at = now
        locked_schedule.next_run_at= compute_next_run_at(
            previous_run_at=now,
            interval_seconds=locked_schedule.interval_seconds,
        )
        locked_schedule.save(update_fields=["last_enqueued_at", "next_run_at"])

    logger.info(
        "Scheduled task enqueued",
        extra={
            "schedule_id": str(locked_schedule.id),
            "schedule_name": locked_schedule.name,
            "task_path": locked_schedule.task_path,
            "queue_name": queue_name,
            "next_run_at": locked_schedule.next_run_at.isoformat() if locked_schedule.next_run_at else None,
        },
    )
    return True


def run_due_schedules(schedules, *, now=None, batch_size=100):
    """
    The main entrance for scheduled tasks, should be called by a management command.
    Dispatch at most 'batch_size' due schedules.
    In other words, batch_size is the maximum number of schedules in a single run.

    'schedules' is expected to be a queryset or iterable of schedule records.
    """
    now = now or timezone.now()

    with acquire_scheduler_lock() as lock:

        # Prevent task to be run twice
        if not _lock_is_acquired(lock):
            logger.info("Scheduler dispatch skipped because another scheduler holds the lock")
            return SchedulerRunResult(scanned=0, enqueued=0, skipped=0)

        due_schedules = list(
            schedules.filter(is_enabled=True, next_run_at__lte=now)
            .order_by("next_run_at")[:batch_size]
        )

        enqueued = 0
        skipped = 0

        for schedule in due_schedules:
            dispatched = dispatch_schedule(schedule=schedule, now=now)
            # a schedule may not be dispatched
            if dispatched:
                enqueued += 1
            else:
                skipped += 1

        return SchedulerRunResult(scanned=len(due_schedules), enqueued=enqueued, skipped=skipped)


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
