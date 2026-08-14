"""
Custom exception classes for each pipeline stage + FastAPI exception handlers.
Every stage raises a typed exception so the orchestrator can set a clear error message.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ─── Pipeline stage exceptions ───────────────────────────────────────────────────

class PipelineError(Exception):
    """Base class for all pipeline errors."""
    stage: str = "unknown"

    def __init__(self, message: str, job_id: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.job_id = job_id


class DownloadError(PipelineError):
    """Raised when yt-dlp download or ffmpeg audio extraction fails."""
    stage = "download"


class TranscriptionError(PipelineError):
    """Raised when Whisper transcription fails."""
    stage = "transcribe"


class TranslationError(PipelineError):
    """Raised when translation (IndicTrans2 or NLLB) fails."""
    stage = "translate"


class SynthesisError(PipelineError):
    """Raised when edge-tts synthesis or time-stretching fails."""
    stage = "synthesize"


class RemixError(PipelineError):
    """Raised when ffmpeg audio/video muxing fails."""
    stage = "remix"


# ─── HTTP-level exceptions ────────────────────────────────────────────────────────

class JobNotFoundError(Exception):
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Job {job_id!r} not found")


class JobNotCompletedError(Exception):
    def __init__(self, job_id: str, status: str) -> None:
        self.job_id = job_id
        self.status = status
        super().__init__(f"Job {job_id!r} is not completed (current status: {status})")


# ─── FastAPI exception handlers ───────────────────────────────────────────────────

def _job_not_found_handler(request: Request, exc: JobNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": f"Job '{exc.job_id}' not found."},
    )


def _job_not_completed_handler(request: Request, exc: JobNotCompletedError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "detail": f"Job '{exc.job_id}' is not ready for download (status: {exc.status})."
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""
    app.add_exception_handler(JobNotFoundError, _job_not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(JobNotCompletedError, _job_not_completed_handler)  # type: ignore[arg-type]
