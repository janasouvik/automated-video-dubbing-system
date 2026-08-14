"""Stage timing helpers."""
from __future__ import annotations

import time
from typing import Any


class StageTimer:
    """Context manager that records wall-clock duration of a pipeline stage."""

    def __init__(self) -> None:
        self.start: float = 0.0
        self.end: float = 0.0
        self.duration: float = 0.0

    def __enter__(self) -> "StageTimer":
        self.start = time.monotonic()
        return self

    def __exit__(self, *args: Any) -> None:
        self.end = time.monotonic()
        self.duration = self.end - self.start
