"""
Pydantic v2 schemas for all API request and response bodies.
These are pure data-transfer objects — no DB logic here.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, Field, field_validator

from app.models.enums import JobStatus


# ─── Request Bodies ───────────────────────────────────────────────────────────────

class JobCreateRequest(BaseModel):
    """Body for POST /jobs — submit a new dubbing job."""
    youtube_url: str = Field(..., description="Full YouTube video URL to dub.")
    target_language: str = Field(default="en", description="Target language (fixed to 'en' per assignment).")
    user_email: Optional[str] = Field(default=None, description="Optional user email to associate job with user in DB.")

    @field_validator("youtube_url")
    @classmethod
    def _validate_youtube_url(cls, v: str) -> str:
        lowered = v.lower()
        if not any(token in lowered for token in ("youtube.com/watch", "youtu.be/", "youtube.com/shorts", "youtube.com/embed")):
            raise ValueError("Must be a valid YouTube URL (youtube.com/watch?v=... or youtu.be/...)")
        return v.strip()


# ─── Response Bodies ──────────────────────────────────────────────────────────────

class JobCreatedResponse(BaseModel):
    """Response for POST /jobs (202 Accepted)."""
    job_id: str
    status: JobStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class StageTimings(BaseModel):
    """Stage timing breakdown in seconds."""
    download_sec: Optional[float] = None
    transcribe_sec: Optional[float] = None
    translate_sec: Optional[float] = None
    synthesize_sec: Optional[float] = None
    remix_sec: Optional[float] = None


class JobStatusResponse(BaseModel):
    """Response for GET /jobs/{job_id}."""
    job_id: str
    youtube_url: str
    status: JobStatus
    progress_percent: int
    current_stage_message: Optional[str] = None
    source_language: Optional[str] = None
    target_language: str
    video_duration_sec: Optional[float] = None
    total_processing_sec: Optional[float] = None
    stage_timings: StageTimings
    error: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class JobListItem(BaseModel):
    """Summary of a job stored in PostgreSQL."""
    job_id: str
    youtube_url: str
    status: JobStatus
    progress_percent: int
    current_stage_message: Optional[str] = None
    source_language: Optional[str] = None
    target_language: str = "en"
    video_duration_sec: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Response for GET /jobs."""
    total: int
    jobs: list[JobListItem]


# ─── Internal pipeline data models ────────────────────────────────────────────────

class TranscriptSegment(BaseModel):
    """One segment from Whisper transcription output."""
    segment_index: int
    start: float          # seconds
    end: float            # seconds
    text: str
    confidence: Optional[float] = None
    speaker: Optional[str] = None   # populated only if diarization is used


class TranslatedSegment(BaseModel):
    """One segment after translation (paired with a TranscriptSegment)."""
    segment_index: int
    start: float
    end: float
    original_text: str
    english_text: str
    engine_used: str


class TTSSegmentMeta(BaseModel):
    """Metadata for one synthesized TTS segment."""
    segment_index: int
    start: float
    end: float
    audio_path: str
    original_duration_sec: float
    target_duration_sec: float
    time_stretch_factor: float
    voice_id: str
    engine_used: str


# ─── Health ───────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    db: str
