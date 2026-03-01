"""Site-wide settings stored in DB.

Supports boolean "toggles" and string config values.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import Base


class SiteSetting(Base):
    __tablename__ = "site_settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    bool_value: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    str_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
