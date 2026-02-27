"""Supplier service layer."""
from __future__ import annotations

import logging
from typing import Optional
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.category import Category
from app.models.supplier import Supplier, SupplierService
from app.models.user import User
from app.schemas.supplier_schema import SupplierCreate, SupplierServiceCreate, SupplierServiceUpdate


logger = logging.getLogger(__name__)


def _normalized_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.strip().split())
    return normalized or None


def _validate_item_identity(item_name: str | None) -> None:
    if not item_name:
        raise ValidationError("Item name is required")


def sync_supplier_id_sequence(db: Session) -> None:
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return
    db.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('suppliers', 'id'), "
            "COALESCE((SELECT MAX(id) FROM suppliers), 0) + 1, false)"
        )
    )


def seed_default_categories(db: Session) -> None:
    defaults = [
        {"key": "building_material", "name": "Building Materials", "is_enabled": True},
        {"key": "vehicle_booking", "name": "Vehicle Booking", "is_enabled": True},
        {"key": "agriculture_supplies", "name": "Agriculture Supplies", "is_enabled": False},
        {"key": "equipment_rental", "name": "Equipment Rental", "is_enabled": False},
        {"key": "local_services", "name": "Local Services", "is_enabled": False},
    ]
    for row in defaults:
        exists = (
            db.query(Category)
            .filter((Category.key == row["key"]) | (Category.name == row["name"]))
            .first()
        )
        if exists:
            changed = False
            if getattr(exists, "key", None) != row["key"]:
                exists.key = row["key"]
                changed = True
            if exists.name != row["name"]:
                exists.name = row["name"]
                changed = True
            if getattr(exists, "is_enabled", True) != row["is_enabled"]:
                exists.is_enabled = row["is_enabled"]
                changed = True
            if changed:
                logger.info(
                    "Default category updated id=%s key=%s enabled=%s",
                    exists.id,
                    exists.key,
                    exists.is_enabled,
                )
            continue

        db.add(Category(key=row["key"], name=row["name"], is_enabled=row["is_enabled"]))
        logger.info(
            "Default category seeded key=%s name=%s enabled=%s",
            row["key"],
            row["name"],
            row["is_enabled"],
        )
    db.commit()


def create_supplier_profile(db: Session, user: User, payload: SupplierCreate) -> Supplier:
    supplier_id = None
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        sync_supplier_id_sequence(db)
        supplier_id = db.execute(
            text("SELECT nextval(pg_get_serial_sequence('suppliers', 'id'))")
        ).scalar_one()

    supplier = Supplier(
        id=int(supplier_id) if supplier_id is not None else None,
        user_id=user.id,
        business_name=payload.business_name,
        phone=payload.phone,
        address=payload.address,
        approved=False,
        blocked=False,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    logger.info("Supplier profile created user_id=%s supplier_id=%s", user.id, supplier.id)
    return supplier


def latest_supplier_profile_for_user(db: Session, user_id: int) -> Supplier | None:
    return (
        db.query(Supplier)
        .filter(Supplier.user_id == user_id)
        .order_by(Supplier.id.desc())
        .first()
    )


def supplier_ids_for_user(db: Session, user_id: int) -> list[int]:
    rows = db.query(Supplier.id).filter(Supplier.user_id == user_id).all()
    return [row[0] for row in rows]


def list_supplier_profiles_for_user(db: Session, user: User) -> list[Supplier]:
    if user.role == "admin":
        return db.query(Supplier).order_by(Supplier.id.desc()).all()
    return (
        db.query(Supplier)
        .filter(Supplier.user_id == user.id)
        .order_by(Supplier.id.desc())
        .all()
    )


def update_supplier_profile(db: Session, user: User, supplier_id: int, payload: SupplierCreate) -> Supplier:
    query = db.query(Supplier).filter(Supplier.id == supplier_id)
    if user.role != "admin":
        query = query.filter(Supplier.user_id == user.id)
    supplier = query.first()
    if not supplier:
        raise NotFoundError("Supplier profile not found")

    supplier.business_name = payload.business_name
    supplier.phone = payload.phone
    supplier.address = payload.address
    db.commit()
    db.refresh(supplier)
    logger.info("Supplier profile updated user_id=%s supplier_id=%s", user.id, supplier.id)
    return supplier


def add_supplier_service(db: Session, user: User, payload: SupplierServiceCreate) -> SupplierService:
    supplier = latest_supplier_profile_for_user(db, user.id)
    if not supplier:
        raise NotFoundError("Supplier profile not found")

    if payload.category_id is not None:
        category = db.query(Category).filter(Category.id == payload.category_id).first()
        if not category:
            raise NotFoundError("Invalid category")
        if getattr(category, "is_enabled", True) is False and user.role != "admin":
            raise ValidationError("Category is coming soon")

    item_name = _normalized_optional_text(payload.item_name)
    item_details = _normalized_optional_text(payload.item_details)
    item_variant = _normalized_optional_text(payload.item_variant)
    _validate_item_identity(item_name)

    service = SupplierService(
        supplier_id=supplier.id,
        category_id=payload.category_id,
        item_name=item_name,
        item_details=item_details,
        item_variant=item_variant,
        photo_url_1=_normalized_optional_text(payload.photo_url_1),
        photo_url_2=_normalized_optional_text(payload.photo_url_2),
        photo_url_3=_normalized_optional_text(payload.photo_url_3),
        price=payload.price,
        availability=_normalized_optional_text(payload.availability) or "available",
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    logger.info(
        "Supplier service added supplier_id=%s category_id=%s service_id=%s",
        supplier.id,
        payload.category_id,
        service.id,
    )
    return service


def list_supplier_services_for_user(db: Session, user: User) -> list[SupplierService]:
    if user.role == "admin":
        return db.query(SupplierService).order_by(SupplierService.id.desc()).all()

    ids = supplier_ids_for_user(db, user.id)
    if not ids:
        return []
    return (
        db.query(SupplierService)
        .filter(SupplierService.supplier_id.in_(ids))
        .order_by(SupplierService.id.desc())
        .all()
    )


def update_supplier_service(
    db: Session,
    user: User,
    service_id: int,
    payload: SupplierServiceUpdate,
) -> SupplierService:
    query = db.query(SupplierService).filter(SupplierService.id == service_id)
    if user.role != "admin":
        ids = supplier_ids_for_user(db, user.id)
        if not ids:
            raise NotFoundError("Supplier profile not found")
        query = query.filter(SupplierService.supplier_id.in_(ids))
    service = query.first()
    if not service:
        raise NotFoundError("Supplier service not found")

    if payload.category_id is not None:
        category = db.query(Category).filter(Category.id == payload.category_id).first()
        if not category:
            raise NotFoundError("Invalid category")
        service.category_id = payload.category_id

    if payload.item_name is not None:
        service.item_name = _normalized_optional_text(payload.item_name)

    if payload.item_details is not None:
        service.item_details = _normalized_optional_text(payload.item_details)

    if payload.item_variant is not None:
        service.item_variant = _normalized_optional_text(payload.item_variant)

    if payload.photo_url_1 is not None:
        service.photo_url_1 = _normalized_optional_text(payload.photo_url_1)

    if payload.photo_url_2 is not None:
        service.photo_url_2 = _normalized_optional_text(payload.photo_url_2)

    if payload.photo_url_3 is not None:
        service.photo_url_3 = _normalized_optional_text(payload.photo_url_3)

    if payload.price is not None:
        service.price = payload.price

    if payload.availability is not None:
        service.availability = _normalized_optional_text(payload.availability) or "available"

    _validate_item_identity(service.item_name)

    db.commit()
    db.refresh(service)
    logger.info("Supplier service updated user_id=%s service_id=%s", user.id, service.id)
    return service


def delete_supplier_service(db: Session, user: User, service_id: int) -> None:
    query = db.query(SupplierService).filter(SupplierService.id == service_id)
    if user.role != "admin":
        ids = supplier_ids_for_user(db, user.id)
        if not ids:
            raise NotFoundError("Supplier profile not found")
        query = query.filter(SupplierService.supplier_id.in_(ids))

    service = query.first()
    if not service:
        raise NotFoundError("Supplier service not found")

    db.delete(service)
    db.commit()
    logger.info("Supplier service deleted user_id=%s service_id=%s", user.id, service_id)


def search_suppliers(
    db: Session,
    category_id: Optional[int] = None,
    query_text: Optional[str] = None,
) -> list[Supplier]:
    normalized_query = " ".join((query_text or "").split())
    query_tokens = [token for token in normalized_query.split(" ") if token][:6]

    query = (
        db.query(Supplier)
        .join(SupplierService, Supplier.id == SupplierService.supplier_id)
        .outerjoin(Category, SupplierService.category_id == Category.id)
        .filter(
            Supplier.approved.is_(True),
            Supplier.blocked.is_(False),
            SupplierService.item_name.isnot(None),
            SupplierService.item_name != "",
        )
    )

    if category_id is not None:
        query = query.filter(SupplierService.category_id == category_id)

    for token in query_tokens:
        term = f"%{token}%"
        query = query.filter(
            or_(
                Supplier.business_name.ilike(term),
                Supplier.address.ilike(term),
                Supplier.phone.ilike(term),
                SupplierService.item_name.ilike(term),
                SupplierService.item_details.ilike(term),
                SupplierService.item_variant.ilike(term),
                SupplierService.availability.ilike(term),
                Category.name.ilike(term),
            )
        )

    return query.distinct().order_by(Supplier.id.asc()).all()
