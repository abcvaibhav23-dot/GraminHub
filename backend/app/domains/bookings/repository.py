"""Bookings domain repository (v2)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domains.bookings.models import V2Booking, V2BookingEvent


class BookingRepository:
    def __init__(self, db: Session, *, tenant_id: str):
        self._db = db
        self._tenant_id = tenant_id

    def add_booking(self, booking: V2Booking) -> V2Booking:
        self._db.add(booking)
        self._db.commit()
        self._db.refresh(booking)
        return booking

    def add_event(self, event: V2BookingEvent) -> V2BookingEvent:
        self._db.add(event)
        self._db.commit()
        self._db.refresh(event)
        return event

    def get(self, booking_id: int) -> V2Booking | None:
        return (
            self._db.query(V2Booking)
            .filter(V2Booking.tenant_id == self._tenant_id, V2Booking.id == booking_id)
            .first()
        )

    def list_for_buyer(self, buyer_user_id: int) -> list[V2Booking]:
        return (
            self._db.query(V2Booking)
            .filter(V2Booking.tenant_id == self._tenant_id, V2Booking.buyer_user_id == buyer_user_id)
            .order_by(V2Booking.created_at.desc())
            .all()
        )

    def list_for_supplier(self, supplier_id: int) -> list[V2Booking]:
        return (
            self._db.query(V2Booking)
            .filter(V2Booking.tenant_id == self._tenant_id, V2Booking.supplier_id == supplier_id)
            .order_by(V2Booking.created_at.desc())
            .all()
        )

    def list_events(self, booking_id: int) -> list[V2BookingEvent]:
        return (
            self._db.query(V2BookingEvent)
            .filter(V2BookingEvent.tenant_id == self._tenant_id, V2BookingEvent.booking_id == booking_id)
            .order_by(V2BookingEvent.created_at.asc())
            .all()
        )
