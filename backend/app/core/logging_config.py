"""Application logging configuration."""
from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import LOG_DIR
from app.core.request_context import get_request_id


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
            "request_id": get_request_id(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> None:
    log_file: Path = LOG_DIR / "app.log"
    handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(JsonFormatter())

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] [req:%(request_id)s] %(name)s: %(message)s")
    )

    class RequestIdFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
            record.request_id = get_request_id()
            return True

    request_id_filter = RequestIdFilter()
    handler.addFilter(request_id_filter)
    console.addFilter(request_id_filter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
    root.addHandler(console)
