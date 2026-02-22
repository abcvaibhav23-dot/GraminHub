"""Booking routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.schemas.booking_schema import BookingCreate, BookingOut, GuestBookingCreate, WhatsAppBookingOut
from app.services.booking_service import (
    create_booking,
    create_guest_booking,
    create_guest_whatsapp_booking,
    create_whatsapp_booking,
    list_user_bookings,
)


router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut)
def create_booking_endpoint(
    payload: BookingCreate,
    current_user: User = Depends(require_roles("user", "supplier", "admin")),
    db: Session = Depends(get_db),
) -> BookingOut:
    return create_booking(db, current_user, payload)


@router.get("/mine", response_model=list[BookingOut])
def list_my_bookings_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BookingOut]:
    return list_user_bookings(db, current_user)


@router.post("/guest", response_model=BookingOut)
def create_guest_booking_endpoint(
    payload: GuestBookingCreate,
    db: Session = Depends(get_db),
) -> BookingOut:
    return create_guest_booking(db, payload)


@router.post("/whatsapp", response_model=WhatsAppBookingOut)
def create_whatsapp_booking_endpoint(
    payload: BookingCreate,
    current_user: User = Depends(require_roles("user", "supplier", "admin")),
    db: Session = Depends(get_db),
) -> WhatsAppBookingOut:
    booking, phone, whatsapp_url = create_whatsapp_booking(db, current_user, payload)
    return WhatsAppBookingOut(
        booking_id=booking.id,
        supplier_id=booking.supplier_id,
        status=booking.status,
        phone=phone,
        whatsapp_url=whatsapp_url,
    )


@router.post("/guest/whatsapp", response_model=WhatsAppBookingOut)
def create_guest_whatsapp_booking_endpoint(
    payload: GuestBookingCreate,
    db: Session = Depends(get_db),
) -> WhatsAppBookingOut:
    booking, phone, whatsapp_url = create_guest_whatsapp_booking(db, payload)
    return WhatsAppBookingOut(
        booking_id=booking.id,
        supplier_id=booking.supplier_id,
        status=booking.status,
        phone=phone,
        whatsapp_url=whatsapp_url,
    )
