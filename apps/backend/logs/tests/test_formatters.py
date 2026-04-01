import logging
import sys

from core.tests.testcases import BaseTestCase
from logs.logging.context import add_log_context, clear_log_context
from logs.logging.formatters import RuntimeFormatter


class RuntimeFormatterTests(BaseTestCase):
    def setUp(self):
        self.formatter = RuntimeFormatter(datefmt="%Y-%m-%d %H:%M:%S")

    def tearDown(self):
        clear_log_context()
        super().tearDown()

    def make_record(self, *, msg="hello world", level=logging.INFO):
        return logging.LogRecord(
            name="test.logger",
            level=level,
            pathname=__file__,
            lineno=1,
            msg=msg,
            args=(),
            exc_info=None,
        )

    def test_format_includes_message_without_context_or_extra(self):
        record = self.make_record()

        result = self.formatter.format(record)

        self.assertIn("INFO", result)
        self.assertIn("test.logger", result)
        self.assertIn("hello world", result)

    def test_format_includes_whitelisted_context_fields(self):
        record = self.make_record()
        add_log_context(request_id="req-123")

        result = self.formatter.format(record)

        self.assertIn("request_id=req-123", result)

    def test_format_includes_whitelisted_extra_fields(self):
        record = self.make_record()
        record.event_type = "Approve"
        record.actor_id = "user-1"
        record.event_id = "event-1"

        result = self.formatter.format(record)

        self.assertIn("event_type=Approve", result)
        self.assertIn("actor_id=user-1", result)
        self.assertIn("event_id=event-1", result)

    def test_format_excludes_non_whitelisted_extra_fields(self):
        record = self.make_record()
        record.action = "approve"

        result = self.formatter.format(record)

        self.assertNotIn("action=approve", result)

    def test_format_appends_exception_traceback(self):
        record = self.make_record(msg="request failed", level=logging.ERROR)

        try:
            raise ValueError("boom")
        except ValueError:
            record.exc_info = sys.exc_info()

        result = self.formatter.format(record)

        self.assertIn("ERROR", result)
        self.assertIn("request failed", result)
        self.assertIn("ValueError: boom", result)
