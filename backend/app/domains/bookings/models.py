"""Bookings domain models (v2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db import Base
from app.domains.bookings.state_machine import BookingState


class V2Booking(Base):
    __tablename__ = "v2_bookings"
    __table_args__ = (
        Index("ix_v2_bookings_tenant_buyer", "tenant_id", "buyer_user_id"),
        Index("ix_v2_bookings_tenant_supplier", "tenant_id", "supplier_id"),
        Index("ix_v2_bookings_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    buyer_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(40), nullable=False, default=BookingState.CREATED.value)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    events = relationship("V2BookingEvent", back_populates="booking", cascade="all, delete-orphan")


class V2BookingEvent(Base):
    __tablename__ = "v2_booking_events"
    __table_args__ = (
        Index("ix_v2_booking_events_tenant_booking", "tenant_id", "booking_id"),
        Index("ix_v2_booking_events_tenant_created", "tenant_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("v2_bookings.id", ondelete="CASCADE"), nullable=False)

    action: Mapped[str] = mapped_column(String(40), nullable=False)
    from_state: Mapped[str | None] = mapped_column(String(40), nullable=True)
    to_state: Mapped[str] = mapped_column(String(40), nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    booking = relationship("V2Booking", back_populates="events")
