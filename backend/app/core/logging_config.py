"""
Structured logging configuration using Python stdlib logging.
All application logs are emitted as structured key-value pairs for easy parsing.
"""
from __future__ import annotations

import logging
import sys
from typing import Any


class _StructuredFormatter(logging.Formatter):
    """Emit log records as structured key=value strings."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        base = super().format(record)
        extras: list[str] = []
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            ):
                extras.append(f"{key}={value!r}")
        if extras:
            return f"{base} | {' '.join(extras)}"
        return base


def configure_logging(debug: bool = False) -> None:
    """Call once at application startup to configure root and app loggers."""
    log_level = logging.DEBUG if debug else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(
        _StructuredFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )

    # Root logger
    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "multipart", "asyncio", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger — use in every module instead of print()."""
    return logging.getLogger(name)
