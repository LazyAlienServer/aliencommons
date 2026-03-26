import json
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler


class StructuredRuntimeFileHandler(TimedRotatingFileHandler):
    """
    A thin project-specific file handler for backend runtime logs.

    Features:
    - auto-create parent directory
    - daily rotation
    - retention via backupCount
    - utf-8 encoding
    - optional JSON line output
    """

    def __init__(
        self, filename, *,
        when="midnight", interval=1, backup_count=30, encoding="utf-8",
        delay=True, utc=True, as_json=True,
        **kwargs,
    ):
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.as_json = as_json

        super().__init__(
            filename=str(path),
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding=encoding,
            delay=delay,
            utc=utc,
            **kwargs,
        )

    def emit(self, record):
        try:
            if self.as_json:
                message = self.format_json_record(record)
                stream = self.stream
                if stream is None:
                    stream = self._open()
                    self.stream = stream

                stream.write(message + self.terminator)
                self.flush()
            else:
                super().emit(record)
        except Exception:
            self.handleError(record)

    def format_json_record(self, record):
        payload = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "pathname": record.pathname,
            "lineno": record.lineno,
        }

        for key in (
            "request_id",
            "user_id",
            "task_name",
            "task_id",
            "queue_name",
            "service",
            "environment",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatter.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)
