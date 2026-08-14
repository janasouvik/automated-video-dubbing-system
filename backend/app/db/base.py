"""Import aggregator for SQLAlchemy Base — used by Alembic env.py."""
from app.models.db_models import Base  # noqa: F401 — re-export for Alembic

__all__ = ["Base"]
