"""JSON logs on stderr. One object per line.

The ROI path attaches extra context under ``structured``. The decision kit
attaches fields on the record and drops secret-like names.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

_SECRET_KEYS = {"api_key", "authorization", "token", "password"}
_LOGGER_NAME = "roi_and_build_vs_buy"


class JsonFormatter(logging.Formatter):
    """Format a log record as a single JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        structured = getattr(record, "structured", None)
        if isinstance(structured, dict):
            payload["data"] = structured
        fields = getattr(record, "fields", None)
        if isinstance(fields, dict):
            for key, value in fields.items():
                if key in _SECRET_KEYS:
                    continue
                payload[str(key)] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, sort_keys=True)


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Attach one JSON handler and return the package logger."""

    logger = logging.getLogger(_LOGGER_NAME)
    logger.handlers.clear()
    logger.setLevel(level.upper())
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, message: str, **fields: object) -> None:
    """Log a message with structured fields. Secret-like keys are dropped."""

    logger.info(message, extra={"fields": fields})
