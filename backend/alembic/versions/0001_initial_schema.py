"""
Initial database schema migration.
Generated from db.txt DDL — creates all ENUMs and tables in dependency order.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Extensions ────────────────────────────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ── ENUM types ────────────────────────────────────────────────────────────────
    job_status = postgresql.ENUM(
        "queued", "downloading", "transcribing", "translating",
        "synthesizing", "remixing", "completed", "failed", "cancelled",
        name="job_status",
    )
    job_status.create(op.get_bind(), checkfirst=True)

    pipeline_stage = postgresql.ENUM(
        "download", "transcribe", "translate", "synthesize", "remix",
        name="pipeline_stage",
    )
    pipeline_stage.create(op.get_bind(), checkfirst=True)

    tts_engine = postgresql.ENUM("edge_tts", "xtts_cloned", name="tts_engine")
    tts_engine.create(op.get_bind(), checkfirst=True)

    translation_engine = postgresql.ENUM(
        "indictrans2", "nllb200", "marian_mt", name="translation_engine"
    )
    translation_engine.create(op.get_bind(), checkfirst=True)

    # ── users ─────────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="TRUE"),
    )

    # ── jobs ──────────────────────────────────────────────────────────────────────
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("youtube_url", sa.Text, nullable=False),
        sa.Column("source_language", sa.String(10), nullable=True),
        sa.Column("target_language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("status", sa.Enum(name="job_status"), nullable=False,
                  server_default="queued"),
        sa.Column("progress_percent", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("current_stage_message", sa.Text, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("video_duration_sec", sa.Numeric(10, 2), nullable=True),
        sa.Column("raw_video_path", sa.Text, nullable=True),
        sa.Column("final_video_path", sa.Text, nullable=True),
        sa.Column("use_diarization", sa.Boolean, nullable=False, server_default="FALSE"),
        sa.Column("use_voice_cloning", sa.Boolean, nullable=False, server_default="FALSE"),
        sa.Column("total_processing_sec", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("progress_percent BETWEEN 0 AND 100"),
    )
    op.create_index("idx_jobs_status", "jobs", ["status"])
    op.create_index("idx_jobs_created_at", "jobs", [sa.text("created_at DESC")])
    op.create_index("idx_jobs_user_id", "jobs", ["user_id"])

    # Trigger for auto-updating updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    op.execute("""
        CREATE TRIGGER trg_jobs_updated_at
        BEFORE UPDATE ON jobs
        FOR EACH ROW EXECUTE FUNCTION set_updated_at()
    """)

    # ── job_stage_events ──────────────────────────────────────────────────────────
    op.create_table(
        "job_stage_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.Enum(name="pipeline_stage"), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_sec", sa.Numeric(10, 2), nullable=True),
        sa.Column("is_error", sa.Boolean, nullable=False, server_default="FALSE"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_stage_events_job_id", "job_stage_events", ["job_id"])
    op.create_index("idx_stage_events_stage", "job_stage_events", ["job_id", "stage"])

    # ── speakers ──────────────────────────────────────────────────────────────────
    op.create_table(
        "speakers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("speaker_label", sa.String(50), nullable=False),
        sa.Column("detected_gender", sa.String(10), nullable=True),
        sa.Column("assigned_tts_voice", sa.String(100), nullable=True),
        sa.Column("reference_clip_path", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("job_id", "speaker_label"),
    )
    op.create_index("idx_speakers_job_id", "speakers", ["job_id"])

    # ── transcript_segments ───────────────────────────────────────────────────────
    op.create_table(
        "transcript_segments",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("speaker_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("speakers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("segment_index", sa.Integer, nullable=False),
        sa.Column("start_sec", sa.Numeric(10, 3), nullable=False),
        sa.Column("end_sec", sa.Numeric(10, 3), nullable=False),
        sa.Column("original_text", sa.Text, nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("job_id", "segment_index"),
        sa.CheckConstraint("end_sec > start_sec"),
    )
    op.create_index("idx_transcript_job_id", "transcript_segments", ["job_id", "segment_index"])

    # ── translation_segments ──────────────────────────────────────────────────────
    op.create_table(
        "translation_segments",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("transcript_segment_id", sa.BigInteger,
                  sa.ForeignKey("transcript_segments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_used", sa.Enum(name="translation_engine"), nullable=False),
        sa.Column("english_text", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("transcript_segment_id"),
    )
    op.create_index("idx_translation_job_id", "translation_segments", ["job_id"])

    # ── tts_segments ──────────────────────────────────────────────────────────────
    op.create_table(
        "tts_segments",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("translation_segment_id", sa.BigInteger,
                  sa.ForeignKey("translation_segments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_used", sa.Enum(name="tts_engine"), nullable=False),
        sa.Column("voice_id", sa.String(100), nullable=True),
        sa.Column("audio_file_path", sa.Text, nullable=False),
        sa.Column("original_duration_sec", sa.Numeric(10, 3), nullable=True),
        sa.Column("target_duration_sec", sa.Numeric(10, 3), nullable=True),
        sa.Column("time_stretch_factor", sa.Numeric(5, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("translation_segment_id"),
    )
    op.create_index("idx_tts_job_id", "tts_segments", ["job_id"])

    # ── job_outputs ───────────────────────────────────────────────────────────────
    op.create_table(
        "job_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("final_video_path", sa.Text, nullable=False),
        sa.Column("final_video_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("video_codec", sa.String(50), nullable=True),
        sa.Column("audio_codec", sa.String(50), nullable=True),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("job_outputs")
    op.drop_table("tts_segments")
    op.drop_table("translation_segments")
    op.drop_table("transcript_segments")
    op.drop_table("speakers")
    op.execute("DROP TRIGGER IF EXISTS trg_jobs_updated_at ON jobs")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at")
    op.drop_table("job_stage_events")
    op.drop_table("jobs")
    op.drop_table("users")

    for enum_name in ("job_status", "pipeline_stage", "tts_engine", "translation_engine"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
