import logging
import json
import sys
from datetime import datetime, timezone

# Standard LogRecord fields we don't want to re-emit as extra context
_SKIP_FIELDS = frozenset({
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "taskName",
})


class JSONFormatter(logging.Formatter):
    """Emits one JSON object per log line — easy to parse in CloudWatch / Datadog."""

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()

        entry: dict = {
            "ts":     datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level":  record.levelname,
            "logger": record.name,
            "msg":    record.message,
        }

        # Attach any extra fields passed via extra={...}
        for key, val in record.__dict__.items():
            if key not in _SKIP_FIELDS:
                entry[key] = val

        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)

        return json.dumps(entry)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger with JSON output to stdout."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
