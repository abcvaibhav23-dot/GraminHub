"""Bookings domain router (v2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.exceptions import NotFoundError
from app.core.security import get_current_user
from app.domains.bookings.schemas import BookingCreateIn, BookingEventOut, BookingOut
from app.domains.bookings.repository import BookingRepository
from app.domains.bookings.service import BookingService
from app.domains.suppliers.repository import SupplierRepository
from app.shared.policies import Actor
from app.shared.tenancy import tenant_id_from_request


router = APIRouter(prefix="/api/v2/bookings", tags=["v2-bookings"])


def _service(
    request: Request,
    db: Session,
    current_user: object,
) -> BookingService:
    tenant_id = tenant_id_from_request(request)
    actor = Actor.from_v1_user(current_user, tenant_id=tenant_id)
    return BookingService(db, actor=actor)


@router.post("", response_model=BookingOut)
def create_booking(
    payload: BookingCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> BookingOut:
    service = _service(request, db, current_user)
    return service.create(supplier_id=payload.supplier_id, description=payload.description)


@router.get("/mine", response_model=list[BookingOut])
def list_my_bookings(
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> list[BookingOut]:
    service = _service(request, db, current_user)
    return service.list_mine()


@router.get("/{booking_id}/events", response_model=list[BookingEventOut])
def booking_events(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> list[BookingEventOut]:
    service = _service(request, db, current_user)
    return service.list_events(booking_id)


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> BookingOut:
    service = _service(request, db, current_user)
    return service.cancel(booking_id=booking_id)


def _supplier_owner_user_id(db: Session, *, tenant_id: str, supplier_id: int) -> int:
    supplier = SupplierRepository(db, tenant_id=tenant_id).get(supplier_id)
    if not supplier:
        raise NotFoundError("Supplier not found")
    return int(supplier.owner_user_id)


@router.post("/{booking_id}/accept", response_model=BookingOut)
def supplier_accept_booking(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> BookingOut:
    tenant_id = tenant_id_from_request(request)
    service = _service(request, db, current_user)
    booking = BookingRepository(db, tenant_id=tenant_id).get(booking_id)
    if not booking:
        raise NotFoundError("Booking not found")
    owner_user_id = _supplier_owner_user_id(db, tenant_id=tenant_id, supplier_id=int(booking.supplier_id))
    return service.supplier_accept(booking_id=booking_id, supplier_owner_user_id=owner_user_id)


@router.post("/{booking_id}/start", response_model=BookingOut)
def supplier_start_booking(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> BookingOut:
    tenant_id = tenant_id_from_request(request)
    service = _service(request, db, current_user)
    booking = BookingRepository(db, tenant_id=tenant_id).get(booking_id)
    if not booking:
        raise NotFoundError("Booking not found")
    owner_user_id = _supplier_owner_user_id(db, tenant_id=tenant_id, supplier_id=int(booking.supplier_id))
    return service.supplier_start(booking_id=booking_id, supplier_owner_user_id=owner_user_id)


@router.post("/{booking_id}/complete", response_model=BookingOut)
def supplier_complete_booking(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> BookingOut:
    tenant_id = tenant_id_from_request(request)
    service = _service(request, db, current_user)
    booking = BookingRepository(db, tenant_id=tenant_id).get(booking_id)
    if not booking:
        raise NotFoundError("Booking not found")
    owner_user_id = _supplier_owner_user_id(db, tenant_id=tenant_id, supplier_id=int(booking.supplier_id))
    return service.supplier_complete(booking_id=booking_id, supplier_owner_user_id=owner_user_id)
