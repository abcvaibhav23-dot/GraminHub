"""Supplier public and supplier-role routes."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.exceptions import NotFoundError
from app.core.security import get_current_user, require_roles
from app.models.booking import Booking
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.review_schema import ReviewCreate, ReviewOut
from app.schemas.booking_schema import BookingOut
from app.schemas.supplier_schema import (
    CategoryOut,
    CallResponse,
    SupplierCreate,
    SupplierOut,
    SupplierServiceCreate,
    SupplierServiceOut,
    SupplierServiceUpdate,
)
from app.services.call_service import log_supplier_call
from app.services.review_service import create_or_update_review, list_supplier_reviews, rating_summary
from app.services.supplier_service import (
    add_supplier_service,
    create_supplier_profile,
    list_supplier_profiles_for_user,
    list_supplier_services_for_user,
    search_suppliers,
    supplier_ids_for_user,
    update_supplier_profile,
    update_supplier_service,
)


router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("/categories", response_model=list[CategoryOut])
def list_supplier_categories_endpoint(db: Session = Depends(get_db)) -> list[CategoryOut]:
    return db.query(Category).order_by(Category.name.asc()).all()


@router.get("/search", response_model=list[SupplierOut])
def search_suppliers_endpoint(
    category_id: Optional[int] = Query(default=None),
    q: Optional[str] = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
) -> list[SupplierOut]:
    suppliers = search_suppliers(db, category_id=category_id, query_text=q)
    for supplier in suppliers:
        avg_rating, total_reviews = rating_summary(db, supplier.id)
        supplier.average_rating = round(avg_rating, 2)
        supplier.total_reviews = total_reviews
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier_details_endpoint(supplier_id: int, db: Session = Depends(get_db)) -> SupplierOut:
    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id, Supplier.approved.is_(True), Supplier.blocked.is_(False))
        .first()
    )
    if not supplier:
        raise NotFoundError("Supplier not found")
    avg_rating, total_reviews = rating_summary(db, supplier.id)
    supplier.average_rating = round(avg_rating, 2)
    supplier.total_reviews = total_reviews
    return supplier


@router.post("/{supplier_id}/call", response_model=CallResponse)
def call_supplier(
    supplier_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CallResponse:
    _, supplier = log_supplier_call(db, current_user, supplier_id)
    return CallResponse(supplier_id=supplier.id, phone=supplier.phone)


@router.post("/profile", response_model=SupplierOut)
def create_or_update_profile(
    payload: SupplierCreate,
    current_user: User = Depends(require_roles("supplier", "admin")),
    db: Session = Depends(get_db),
) -> SupplierOut:
    return create_supplier_profile(db, current_user, payload)


@router.get("/me/profiles", response_model=list[SupplierOut])
def list_my_supplier_profiles(
    current_user: User = Depends(require_roles("supplier", "admin")),
    db: Session = Depends(get_db),
) -> list[SupplierOut]:
    return list_supplier_profiles_for_user(db, current_user)


@router.put("/profiles/{supplier_id}", response_model=SupplierOut)
def update_supplier_profile_endpoint(
    supplier_id: int,
    payload: SupplierCreate,
    current_user: User = Depends(require_roles("supplier", "admin")),
    db: Session = Depends(get_db),
) -> SupplierOut:
    return update_supplier_profile(db, current_user, supplier_id, payload)


@router.post("/services", response_model=SupplierServiceOut)
def create_supplier_service_endpoint(
    payload: SupplierServiceCreate,
    current_user: User = Depends(require_roles("supplier", "admin")),
    db: Session = Depends(get_db),
) -> SupplierServiceOut:
    return add_supplier_service(db, current_user, payload)


@router.get("/me/services", response_model=list[SupplierServiceOut])
def list_my_supplier_services(
    current_user: User = Depends(require_roles("supplier", "admin")),
    db: Session = Depends(get_db),
) -> list[SupplierServiceOut]:
    return list_supplier_services_for_user(db, current_user)


@router.put("/services/{service_id}", response_model=SupplierServiceOut)
def update_supplier_service_endpoint(
    service_id: int,
    payload: SupplierServiceUpdate,
    current_user: User = Depends(require_roles("supplier", "admin")),
    db: Session = Depends(get_db),
) -> SupplierServiceOut:
    return update_supplier_service(db, current_user, service_id, payload)


@router.get("/me/bookings", response_model=list[BookingOut])
def my_supplier_bookings(
    current_user: User = Depends(require_roles("supplier", "admin")),
    db: Session = Depends(get_db),
) -> list[BookingOut]:
    supplier_ids = supplier_ids_for_user(db, current_user.id)
    if not supplier_ids:
        raise NotFoundError("Supplier profile not found")

    return (
        db.query(Booking)
        .filter(Booking.supplier_id.in_(supplier_ids))
        .order_by(Booking.created_at.desc())
        .all()
    )


@router.get("/{supplier_id}/reviews", response_model=list[ReviewOut])
def list_supplier_reviews_endpoint(supplier_id: int, db: Session = Depends(get_db)) -> list[ReviewOut]:
    return list_supplier_reviews(db, supplier_id)


@router.post("/{supplier_id}/reviews", response_model=ReviewOut)
def add_supplier_review(
    supplier_id: int,
    payload: ReviewCreate,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
) -> ReviewOut:
    if payload.supplier_id != supplier_id:
        raise HTTPException(status_code=400, detail="Supplier ID mismatch")
    return create_or_update_review(db, current_user, supplier_id, payload)
