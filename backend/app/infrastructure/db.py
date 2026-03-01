"""Database wiring for v2.

For now v2 shares the same SQLAlchemy engine/session/Base as v1, so the app can
incrementally adopt v2 domains without breaking existing v1 endpoints.

Production goal:
- move schema evolution to Alembic migrations (no runtime DDL in `main.py`).
"""
from __future__ import annotations

from app.core.config import Base, SessionLocal, engine, get_db, settings

__all__ = ["Base", "SessionLocal", "engine", "get_db", "settings"]
