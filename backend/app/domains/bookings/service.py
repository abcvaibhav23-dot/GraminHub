"""Bookings domain services (v2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.domains.bookings.models import V2Booking, V2BookingEvent
from app.domains.bookings.policies import can_create_booking, can_supplier_act, can_update_booking
from app.domains.bookings.repository import BookingRepository
from app.domains.bookings.state_machine import BookingAction, BookingState, transition
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.shared.policies import Actor


class BookingService:
    def __init__(self, db: Session, *, actor: Actor):
        self._db = db
        self._actor = actor
        self._repo = BookingRepository(db, tenant_id=actor.tenant_id)

    def create(self, *, supplier_id: int, description: str) -> V2Booking:
        if not can_create_booking(self._actor):
            raise ForbiddenError("Not allowed to create booking")

        booking = V2Booking(
            tenant_id=self._actor.tenant_id,
            buyer_user_id=self._actor.user_id,
            supplier_id=supplier_id,
            status=BookingState.CREATED.value,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        booking = self._repo.add_booking(booking)
        self._repo.add_event(
            V2BookingEvent(
                tenant_id=self._actor.tenant_id,
                booking_id=booking.id,
                action=BookingAction.CREATE.value,
                from_state=None,
                to_state=BookingState.CREATED.value,
                actor_user_id=self._actor.user_id,
                meta=None,
            )
        )

        # Immediately submit for supplier approval (rural UX: booking is "requested").
        return self._apply_action(booking_id=booking.id, action=BookingAction.SUBMIT, supplier_owner_user_id=None)

    def list_mine(self) -> list[V2Booking]:
        return self._repo.list_for_buyer(self._actor.user_id)

    def list_events(self, booking_id: int) -> list[V2BookingEvent]:
        booking = self._repo.get(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if not can_update_booking(self._actor, booking):
            raise ForbiddenError("Not allowed to view booking events")
        return self._repo.list_events(booking_id)

    def get(self, booking_id: int) -> V2Booking:
        booking = self._repo.get(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if not can_update_booking(self._actor, booking):
            raise ForbiddenError("Not allowed to view this booking")
        return booking

    def supplier_accept(self, *, booking_id: int, supplier_owner_user_id: int) -> V2Booking:
        return self._apply_action(
            booking_id=booking_id,
            action=BookingAction.ACCEPT,
            supplier_owner_user_id=supplier_owner_user_id,
        )

    def supplier_start(self, *, booking_id: int, supplier_owner_user_id: int) -> V2Booking:
        return self._apply_action(
            booking_id=booking_id,
            action=BookingAction.START,
            supplier_owner_user_id=supplier_owner_user_id,
        )

    def supplier_complete(self, *, booking_id: int, supplier_owner_user_id: int) -> V2Booking:
        return self._apply_action(
            booking_id=booking_id,
            action=BookingAction.COMPLETE,
            supplier_owner_user_id=supplier_owner_user_id,
        )

    def cancel(self, *, booking_id: int) -> V2Booking:
        return self._apply_action(
            booking_id=booking_id,
            action=BookingAction.CANCEL,
            supplier_owner_user_id=None,
        )

    def _apply_action(
        self,
        *,
        booking_id: int,
        action: BookingAction,
        supplier_owner_user_id: int | None,
    ) -> V2Booking:
        booking = self._repo.get(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")

        if action in {BookingAction.ACCEPT, BookingAction.START, BookingAction.COMPLETE}:
            if supplier_owner_user_id is None:
                raise ValidationError("supplier_owner_user_id is required for supplier action")
            if not can_supplier_act(self._actor, booking, supplier_owner_user_id=supplier_owner_user_id):
                raise ForbiddenError("Not allowed to act on this booking")
        else:
            if not can_update_booking(self._actor, booking):
                raise ForbiddenError("Not allowed to update this booking")

        current = BookingState(booking.status)
        try:
            next_state = transition(current, action)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        booking.status = next_state.value
        booking.updated_at = datetime.utcnow()
        self._db.add(booking)
        self._db.commit()
        self._db.refresh(booking)

        self._repo.add_event(
            V2BookingEvent(
                tenant_id=self._actor.tenant_id,
                booking_id=booking.id,
                action=action.value,
                from_state=current.value,
                to_state=next_state.value,
                actor_user_id=self._actor.user_id,
                meta=None,
            )
        )
        return booking
