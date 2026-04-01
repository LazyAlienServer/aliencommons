import logging

from .context import get_log_context


class RuntimeFormatter(logging.Formatter):
    """
    Format log records as a single readable line.
    """
    CONTEXT_FIELDS_WHITELIST = (
        'request_id',
    )

    EXTRA_FIELDS_WHITELIST = (
        'event_type',
        'actor_id',
        'source_article_id',
        'article_snapshot_id',
        'event_id',
        'task_id',
        'task_name',
        'task_path',
        'queue_name'
    )

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()

        parts = []

        context = get_log_context()
        for field_name in self.CONTEXT_FIELDS_WHITELIST:
            value = context.get(field_name, None)
            if value is not None:
                parts.append(f"{field_name}={value}")

        for field_name in self.EXTRA_FIELDS_WHITELIST:
            value = getattr(record, field_name, None)
            if value is not None:
                parts.append(f"{field_name}={value}")

        context_text = ""
        if parts:
            context_text = " " + " ".join(parts)

        log_line = f"{timestamp} {level} {logger_name}{context_text} {message}"

        if record.exc_info:
            exception_text = self.formatException(record.exc_info)
            log_line = f"{log_line}\n{exception_text}"

        return log_line
