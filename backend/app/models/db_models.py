"""
SQLAlchemy 2.x ORM models — exact Python representation of the PostgreSQL schema
defined in db.txt. All 8 tables are mapped here.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Column, DateTime,
    Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ─── Enum types ────────────────────────────────────────────────────────────────────

class JobStatusEnum(str, enum.Enum):
    queued = "queued"
    downloading = "downloading"
    transcribing = "transcribing"
    translating = "translating"
    synthesizing = "synthesizing"
    remixing = "remixing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class PipelineStageEnum(str, enum.Enum):
    download = "download"
    transcribe = "transcribe"
    translate = "translate"
    synthesize = "synthesize"
    remix = "remix"


class TTSEngineEnum(str, enum.Enum):
    edge_tts = "edge_tts"
    xtts_cloned = "xtts_cloned"


class TranslationEngineEnum(str, enum.Enum):
    indictrans2 = "indictrans2"
    nllb200 = "nllb200"
    marian_mt = "marian_mt"


# ─── Models ────────────────────────────────────────────────────────────────────────

class User(Base):
    """Optional auth table — present for schema completeness, not wired into MVP auth."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="user")


class Job(Base):
    """Core table — one row per dubbing request."""
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    youtube_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    target_language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    status: Mapped[JobStatusEnum] = mapped_column(
        SAEnum(JobStatusEnum, name="job_status"), nullable=False, default=JobStatusEnum.queued
    )
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_stage_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_duration_sec: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    raw_video_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    final_video_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    use_diarization: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    use_voice_cloning: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    total_processing_sec: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="jobs")
    stage_events: Mapped[list["JobStageEvent"]] = relationship("JobStageEvent", back_populates="job", cascade="all, delete-orphan")
    speakers: Mapped[list["Speaker"]] = relationship("Speaker", back_populates="job", cascade="all, delete-orphan")
    transcript_segments: Mapped[list["TranscriptSegment"]] = relationship("TranscriptSegment", back_populates="job", cascade="all, delete-orphan")
    translation_segments: Mapped[list["TranslationSegment"]] = relationship("TranslationSegment", back_populates="job", cascade="all, delete-orphan")
    tts_segments: Mapped[list["TTSSegment"]] = relationship("TTSSegment", back_populates="job", cascade="all, delete-orphan")
    output: Mapped[Optional["JobOutput"]] = relationship("JobOutput", back_populates="job", cascade="all, delete-orphan", uselist=False)


class JobStageEvent(Base):
    """Append-only per-stage timing + progress log."""
    __tablename__ = "job_stage_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    stage: Mapped[PipelineStageEnum] = mapped_column(
        SAEnum(PipelineStageEnum, name="pipeline_stage"), nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_sec: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    is_error: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["Job"] = relationship("Job", back_populates="stage_events")


class Speaker(Base):
    """Diarization speaker table (populated only if USE_DIARIZATION=true)."""
    __tablename__ = "speakers"
    __table_args__ = (UniqueConstraint("job_id", "speaker_label"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    speaker_label: Mapped[str] = mapped_column(String(50), nullable=False)
    detected_gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    assigned_tts_voice: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reference_clip_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["Job"] = relationship("Job", back_populates="speakers")
    transcript_segments: Mapped[list["TranscriptSegment"]] = relationship("TranscriptSegment", back_populates="speaker")


class TranscriptSegment(Base):
    """Whisper transcription output — one row per segment."""
    __tablename__ = "transcript_segments"
    __table_args__ = (
        UniqueConstraint("job_id", "segment_index"),
        CheckConstraint("end_sec > start_sec"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    speaker_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("speakers.id", ondelete="SET NULL"), nullable=True
    )
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_sec: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    end_sec: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["Job"] = relationship("Job", back_populates="transcript_segments")
    speaker: Mapped[Optional["Speaker"]] = relationship("Speaker", back_populates="transcript_segments")
    translation: Mapped[Optional["TranslationSegment"]] = relationship("TranslationSegment", back_populates="transcript_segment", uselist=False)


class TranslationSegment(Base):
    """Translation output — one row per transcript segment."""
    __tablename__ = "translation_segments"
    __table_args__ = (UniqueConstraint("transcript_segment_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    transcript_segment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("transcript_segments.id", ondelete="CASCADE"), nullable=False
    )
    engine_used: Mapped[TranslationEngineEnum] = mapped_column(
        SAEnum(TranslationEngineEnum, name="translation_engine"), nullable=False
    )
    english_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["Job"] = relationship("Job", back_populates="translation_segments")
    transcript_segment: Mapped["TranscriptSegment"] = relationship("TranscriptSegment", back_populates="translation")
    tts_segment: Mapped[Optional["TTSSegment"]] = relationship("TTSSegment", back_populates="translation_segment", uselist=False)


class TTSSegment(Base):
    """Synthesized TTS audio metadata — one row per translation segment."""
    __tablename__ = "tts_segments"
    __table_args__ = (UniqueConstraint("translation_segment_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    translation_segment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("translation_segments.id", ondelete="CASCADE"), nullable=False
    )
    engine_used: Mapped[TTSEngineEnum] = mapped_column(
        SAEnum(TTSEngineEnum, name="tts_engine"), nullable=False
    )
    voice_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    audio_file_path: Mapped[str] = mapped_column(Text, nullable=False)
    original_duration_sec: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    target_duration_sec: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    time_stretch_factor: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["Job"] = relationship("Job", back_populates="tts_segments")
    translation_segment: Mapped["TranslationSegment"] = relationship("TranslationSegment", back_populates="tts_segment")


class JobOutput(Base):
    """Final deliverable metadata — 1:1 with a completed job."""
    __tablename__ = "job_outputs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    final_video_path: Mapped[str] = mapped_column(Text, nullable=False)
    final_video_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    video_codec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    audio_codec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["Job"] = relationship("Job", back_populates="output")
