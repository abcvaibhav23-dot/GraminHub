"""Bookings domain policies (v2)."""

from __future__ import annotations

from app.domains.bookings.models import V2Booking
from app.shared.policies import Actor, is_admin
from app.shared.roles import Role


def can_create_booking(actor: Actor) -> bool:
    return actor.role in {Role.BUYER, Role.ADMIN, Role.SUPER_ADMIN}


def can_update_booking(actor: Actor, booking: V2Booking) -> bool:
    if is_admin(actor):
        return True
    if actor.role == Role.BUYER and booking.buyer_user_id == actor.user_id:
        return True
    return False


def can_supplier_act(actor: Actor, booking: V2Booking, *, supplier_owner_user_id: int) -> bool:
    if is_admin(actor):
        return True
    if actor.role != Role.SUPPLIER:
        return False
    return actor.user_id == supplier_owner_user_id
