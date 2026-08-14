"""
Utility helpers for file and directory management.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def ensure_job_dir(job_id: str) -> Path:
    """Create and return the per-job working directory."""
    job_dir = settings.DATA_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "audio").mkdir(parents=True, exist_ok=True)
    (job_dir / "tts_segments").mkdir(parents=True, exist_ok=True)
    return job_dir


def cleanup_job_dir(job_id: str) -> bool:
    """
    Delete the entire per-job working directory and all artifacts.
    Returns True if the directory existed and was removed, False otherwise.
    """
    job_dir = settings.DATA_DIR / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)
        logger.info("Job directory cleaned up", extra={"job_id": job_id})
        return True
    return False


def safe_unlink(path: Path) -> None:
    """Delete a file without raising if it doesn't exist."""
    try:
        path.unlink(missing_ok=True)
    except Exception as exc:
        logger.warning(f"Failed to delete {path}: {exc}")
