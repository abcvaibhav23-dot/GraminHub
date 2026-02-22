"""Booking schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class BookingCreate(BaseModel):
    supplier_id: int
    description: str = Field(min_length=5, max_length=500)


class GuestBookingCreate(BookingCreate):
    guest_name: str = Field(min_length=2, max_length=120)
    guest_phone: str = Field(min_length=7, max_length=30)


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    supplier_id: int
    status: str
    description: str
    guest_name: Optional[str] = None
    guest_phone: Optional[str] = None
    created_at: datetime


class WhatsAppBookingOut(BaseModel):
    booking_id: int
    supplier_id: int
    status: str
    phone: str
    whatsapp_url: str
