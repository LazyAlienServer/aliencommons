from django.db import IntegrityError
from django.utils import timezone

from core.tests.testcases import BaseTestCase
from tasks.models import IntervalSchedule, PeriodicTask


class IntervalScheduleModelTests(BaseTestCase):
    def test_string_representation_uses_every_and_period(self):
        schedule = IntervalSchedule.objects.create(
            every=5,
            period=IntervalSchedule.Periods.MINUTE,
        )

        self.assertEqual(str(schedule), "every 5 minute")

    def test_in_seconds_returns_expected_value(self):
        hour_schedule = IntervalSchedule.objects.create(
            every=2,
            period=IntervalSchedule.Periods.HOUR,
        )
        millisecond_schedule = IntervalSchedule.objects.create(
            every=500,
            period=IntervalSchedule.Periods.MILLISECOND,
        )

        self.assertEqual(hour_schedule.in_seconds, 7200)
        self.assertEqual(millisecond_schedule.in_seconds, 0.5)

    def test_unique_constraint_prevents_duplicate_schedule(self):
        IntervalSchedule.objects.create(
            every=1,
            period=IntervalSchedule.Periods.DAY,
        )

        with self.assertRaises(IntegrityError):
            IntervalSchedule.objects.create(
                every=1,
                period=IntervalSchedule.Periods.DAY,
            )


class PeriodicTaskModelTests(BaseTestCase):
    def test_string_representation_is_name(self):
        schedule = IntervalSchedule.objects.create(
            every=1,
            period=IntervalSchedule.Periods.MINUTE,
        )
        task = PeriodicTask.objects.create(
            name="cleanup cache",
            task="pages.tasks.refresh_youtube_cache",
            queue_name="maintenance",
            interval=schedule,
            next_enqueue_at=timezone.now(),
        )

        self.assertEqual(str(task), "cleanup cache")

