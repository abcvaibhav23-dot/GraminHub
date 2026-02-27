"""Booking service layer."""
from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import quote
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.booking import Booking
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.booking_schema import BookingCreate, GuestBookingCreate
from app.services.user_service import get_or_create_guest_user
from app.services.site_setting_service import get_site_settings, seed_site_settings
from app.core.exceptions import ForbiddenError


logger = logging.getLogger(__name__)


def _get_approved_supplier(db: Session, supplier_id: int) -> Supplier:
    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id, Supplier.approved.is_(True), Supplier.blocked.is_(False))
        .first()
    )
    if not supplier:
        raise NotFoundError("Supplier not found, not approved, or blocked")
    return supplier


def _normalize_whatsapp_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 10:
        return f"91{digits}"
    return digits


def _create_booking_record(
    db: Session,
    *,
    user_id: int,
    supplier_id: int,
    description: str,
    guest_name: Optional[str] = None,
    guest_phone: Optional[str] = None,
) -> Booking:
    booking = Booking(
        user_id=user_id,
        supplier_id=supplier_id,
        status="pending",
        description=description,
        guest_name=guest_name,
        guest_phone=guest_phone,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def create_booking(db: Session, user: User, payload: BookingCreate) -> Booking:
    supplier = _get_approved_supplier(db, payload.supplier_id)
    booking = _create_booking_record(
        db,
        user_id=user.id,
        supplier_id=supplier.id,
        description=payload.description,
    )
    logger.info("Booking created: booking_id=%s user_id=%s supplier_id=%s", booking.id, user.id, payload.supplier_id)
    return booking


def create_whatsapp_booking(db: Session, user: User, payload: BookingCreate) -> tuple[Booking, str, str]:
    seed_site_settings(db)
    site = get_site_settings(db)
    if not site.get("enable_supplier_whatsapp", True):
        raise ForbiddenError("Supplier WhatsApp is disabled by owner")
    supplier = _get_approved_supplier(db, payload.supplier_id)
    booking = _create_booking_record(
        db,
        user_id=user.id,
        supplier_id=supplier.id,
        description=payload.description,
    )

    wa_phone = _normalize_whatsapp_phone(supplier.phone)
    text = quote(
        f"Hi {supplier.business_name}, I am {user.name}. I want to book: {payload.description}"
    )
    whatsapp_url = f"https://wa.me/{wa_phone}?text={text}"
    logger.info(
        "WhatsApp booking created: booking_id=%s user_id=%s supplier_id=%s",
        booking.id,
        user.id,
        supplier.id,
    )
    return booking, supplier.phone, whatsapp_url


def create_guest_booking(db: Session, payload: GuestBookingCreate) -> Booking:
    supplier = _get_approved_supplier(db, payload.supplier_id)
    guest_user = get_or_create_guest_user(db)
    booking = _create_booking_record(
        db,
        user_id=guest_user.id,
        supplier_id=supplier.id,
        description=payload.description,
        guest_name=payload.guest_name,
        guest_phone=payload.guest_phone,
    )
    logger.info(
        "Guest booking created: booking_id=%s supplier_id=%s guest_phone=%s",
        booking.id,
        supplier.id,
        payload.guest_phone,
    )
    return booking


def create_guest_whatsapp_booking(db: Session, payload: GuestBookingCreate) -> tuple[Booking, str, str]:
    seed_site_settings(db)
    site = get_site_settings(db)
    if not site.get("enable_supplier_whatsapp", True):
        raise ForbiddenError("Supplier WhatsApp is disabled by owner")
    supplier = _get_approved_supplier(db, payload.supplier_id)
    booking = create_guest_booking(db, payload)

    wa_phone = _normalize_whatsapp_phone(supplier.phone)
    text = quote(
        f"Hi {supplier.business_name}, I am {payload.guest_name} ({payload.guest_phone}). "
        f"I want to book: {payload.description}"
    )
    whatsapp_url = f"https://wa.me/{wa_phone}?text={text}"
    return booking, supplier.phone, whatsapp_url


def list_user_bookings(db: Session, user: User) -> list[Booking]:
    return db.query(Booking).filter(Booking.user_id == user.id).order_by(Booking.created_at.desc()).all()
