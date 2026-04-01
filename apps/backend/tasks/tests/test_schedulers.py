from unittest.mock import Mock, patch

from django.utils import timezone

from datetime import timedelta

from core.tests.testcases import BaseTestCase
from tasks.models import IntervalSchedule, PeriodicTask
from tasks.schedulers import SchedulerRunResult, dispatch_task, enqueue_due_tasks


class SchedulerTests(BaseTestCase):
    def create_periodic_task(
        self,
        *,
        name="refresh youtube cache",
        task_path="pages.tasks.refresh_youtube_cache",
        queue_name="maintenance",
        next_enqueue_at=None,
        args=None,
        kwargs=None,
        is_enabled=True,
    ):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.Periods.MINUTE,
        )
        return PeriodicTask.objects.create(
            name=name,
            task=task_path,
            queue_name=queue_name,
            interval=schedule,
            args=args or [],
            kwargs=kwargs or {},
            is_enabled=is_enabled,
            next_enqueue_at=next_enqueue_at or timezone.now(),
        )

    @patch("tasks.schedulers.compute_next_enqueue_at")
    @patch("tasks.schedulers.import_string")
    def test_dispatch_task_enqueues_function_and_updates_schedule(
        self,
        import_string_mock,
        compute_next_enqueue_at_mock,
    ):
        task = self.create_periodic_task(
            args=["alpha"],
            kwargs={"beta": "bravo"},
        )
        now = timezone.now()
        next_enqueue_at = now + timedelta(minutes=1)

        queueing_task = Mock()
        task_function = Mock()
        task_function.using.return_value = queueing_task

        import_string_mock.return_value = task_function
        compute_next_enqueue_at_mock.return_value = next_enqueue_at

        dispatch_task(task=task, now=now)

        task.refresh_from_db()

        import_string_mock.assert_called_once_with("pages.tasks.refresh_youtube_cache")
        task_function.using.assert_called_once_with(queue_name="maintenance")
        queueing_task.enqueue.assert_called_once_with("alpha", beta="bravo")
        compute_next_enqueue_at_mock.assert_called_once_with(
            interval_seconds=task.interval.in_seconds,
        )
        self.assertEqual(task.last_enqueued_at, now)
        self.assertEqual(task.next_enqueue_at, next_enqueue_at)

    @patch("tasks.schedulers.dispatch_task")
    @patch("tasks.schedulers.acquire_scheduler_lock")
    def test_enqueue_due_tasks_dispatches_only_due_tasks_and_returns_summary(
        self,
        acquire_scheduler_lock_mock,
        dispatch_task_mock,
    ):
        lock = Mock()
        lock.__enter__ = Mock(return_value=lock)
        lock.__exit__ = Mock(return_value=False)
        acquire_scheduler_lock_mock.return_value = lock

        now = timezone.now()
        due_task = self.create_periodic_task(
            name="due task",
            next_enqueue_at=now - timedelta(minutes=1),
        )
        self.create_periodic_task(
            name="future task",
            next_enqueue_at=now + timedelta(minutes=1),
        )

        with patch("tasks.schedulers.timezone.now", return_value=now):
            result = enqueue_due_tasks(
                PeriodicTask.objects.filter(is_enabled=True),
            )

        self.assertEqual(
            result,
            SchedulerRunResult(scanned=1, enqueued=1, failed=0),
        )
        dispatch_task_mock.assert_called_once()
        self.assertEqual(dispatch_task_mock.call_args.kwargs["task"].id, due_task.id)
        self.assertEqual(dispatch_task_mock.call_args.kwargs["now"], now)

    @patch("tasks.schedulers.dispatch_task")
    @patch("tasks.schedulers.acquire_scheduler_lock")
    def test_enqueue_due_tasks_counts_failures_without_stopping_batch(
        self,
        acquire_scheduler_lock_mock,
        dispatch_task_mock,
    ):
        lock = Mock()
        lock.__enter__ = Mock(return_value=lock)
        lock.__exit__ = Mock(return_value=False)
        acquire_scheduler_lock_mock.return_value = lock

        now = timezone.now()
        first_task = self.create_periodic_task(
            name="first due task",
            next_enqueue_at=now - timedelta(minutes=2),
        )
        second_task = self.create_periodic_task(
            name="second due task",
            next_enqueue_at=now - timedelta(minutes=1),
        )

        dispatch_task_mock.side_effect = [RuntimeError("boom"), None]

        with patch("tasks.schedulers.timezone.now", return_value=now):
            result = enqueue_due_tasks(
                PeriodicTask.objects.filter(is_enabled=True),
            )

        self.assertEqual(
            result,
            SchedulerRunResult(scanned=2, enqueued=1, failed=1),
        )
        self.assertEqual(dispatch_task_mock.call_count, 2)
        self.assertEqual(dispatch_task_mock.call_args_list[0].kwargs["task"].id, first_task.id)
        self.assertEqual(dispatch_task_mock.call_args_list[1].kwargs["task"].id, second_task.id)
