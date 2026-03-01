"""Bookings domain schemas (v2)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domains.bookings.state_machine import BookingState


class BookingCreateIn(BaseModel):
    supplier_id: int = Field(..., ge=1)
    description: str = Field(..., min_length=3, max_length=500)


class BookingOut(BaseModel):
    id: int
    supplier_id: int
    buyer_user_id: int
    status: BookingState
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookingEventOut(BaseModel):
    id: int
    action: str
    from_state: str | None
    to_state: str
    actor_user_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
