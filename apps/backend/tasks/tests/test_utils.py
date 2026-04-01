from unittest.mock import patch

from django.utils import timezone

from datetime import timedelta

from core.tests.testcases import BaseTestCase
from tasks.utils import compute_next_enqueue_at


class TaskUtilsTests(BaseTestCase):
    @patch("tasks.utils.timezone.now")
    def test_compute_next_enqueue_at_adds_interval_to_current_time(self, now_mock):
        fixed_now = timezone.now()
        now_mock.return_value = fixed_now

        result = compute_next_enqueue_at(interval_seconds=90)

        self.assertEqual(result, fixed_now + timedelta(seconds=90))

    def test_compute_next_enqueue_at_rejects_non_positive_interval(self):
        with self.assertRaises(ValueError) as exc:
            compute_next_enqueue_at(interval_seconds=0)

        self.assertEqual(str(exc.exception), "Interval must be greater than 0")

