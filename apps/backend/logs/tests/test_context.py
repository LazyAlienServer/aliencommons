from core.tests.testcases import BaseTestCase
from logs.logging.context import (
    add_log_context,
    clear_log_context,
    get_log_context,
    remove_log_context,
    set_log_context,
)


class LogContextTests(BaseTestCase):
    def tearDown(self):
        clear_log_context()
        super().tearDown()

    def test_set_log_context_replaces_existing_context(self):
        add_log_context(request_id="req-1", task_id="task-1")

        set_log_context(request_id="req-2")

        self.assertEqual(get_log_context(), {"request_id": "req-2"})

    def test_add_log_context_merges_values(self):
        set_log_context(request_id="req-1")

        add_log_context(task_id="task-1")

        self.assertEqual(
            get_log_context(),
            {
                "request_id": "req-1",
                "task_id": "task-1",
            },
        )

    def test_remove_log_context_deletes_specified_keys(self):
        set_log_context(request_id="req-1", task_id="task-1", queue_name="default")

        remove_log_context("task_id", "queue_name")

        self.assertEqual(get_log_context(), {"request_id": "req-1"})

    def test_clear_log_context_empties_context(self):
        set_log_context(request_id="req-1")

        clear_log_context()

        self.assertEqual(get_log_context(), {})

    def test_get_log_context_returns_a_copy(self):
        set_log_context(request_id="req-1")

        context = get_log_context()
        context["request_id"] = "mutated"

        self.assertEqual(get_log_context(), {"request_id": "req-1"})
