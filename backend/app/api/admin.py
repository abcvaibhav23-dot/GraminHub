"""Admin routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.exceptions import ConflictError
from app.core.security import require_roles
from app.models.booking import Booking
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.booking_schema import BookingOut
from app.schemas.supplier_schema import SupplierCreate
from app.schemas.supplier_schema import SupplierOut
from app.schemas.site_setting_schema import SiteSettingsOut, SiteSettingsUpdate
from app.schemas.user_schema import MessageResponse, UserOut
from app.services.supplier_service import create_supplier_profile, delete_supplier_service
from app.services.site_setting_service import get_site_settings, seed_site_settings, update_site_settings
from app.services.user_service import get_or_create_phone_role_user, normalize_phone


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


class CategoryCreate(BaseModel):
    key: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=2, max_length=100)
    is_enabled: bool = Field(default=False)


def _category_key_from_name(name: str) -> str:
    safe = []
    for ch in name.strip().lower():
        if ch.isalnum():
            safe.append(ch)
        elif ch in {" ", "-", "/"}:
            safe.append("_")
    out = "_".join("".join(safe).split("_"))
    return out[:80] or "category"


class ManagedUserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=20)
    role: str = Field(default="user")


class ManagedSupplierCreate(BaseModel):
    owner_name: str = Field(min_length=2, max_length=120)
    owner_phone: str = Field(min_length=7, max_length=20)
    business_name: str = Field(min_length=2, max_length=150)
    supplier_phone: str = Field(min_length=7, max_length=30)
    address: str = Field(min_length=5, max_length=300)


def _get_supplier_or_404(db: Session, supplier_id: int) -> Supplier:
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users", response_model=list[UserOut])
def list_users_endpoint(
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> list[UserOut]:
    return db.query(User).order_by(User.id.asc()).all()


@router.post("/users", response_model=UserOut)
def create_managed_user_endpoint(
    payload: ManagedUserCreate,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> UserOut:
    safe_role = payload.role.strip().lower()
    if safe_role not in {"user", "supplier"}:
        raise HTTPException(status_code=400, detail="Role must be user or supplier")

    user = get_or_create_phone_role_user(
        db,
        phone=normalize_phone(payload.phone),
        role=safe_role,
        name=payload.name,
    )
    user.blocked = False
    db.commit()
    db.refresh(user)
    logger.info("Managed user created/updated user_id=%s role=%s", user.id, user.role)
    return user


@router.post("/suppliers", response_model=SupplierOut)
def create_managed_supplier_endpoint(
    payload: ManagedSupplierCreate,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> SupplierOut:
    supplier_owner = get_or_create_phone_role_user(
        db,
        phone=normalize_phone(payload.owner_phone),
        role="supplier",
        name=payload.owner_name,
    )
    supplier_owner.blocked = False
    db.commit()
    db.refresh(supplier_owner)

    supplier = create_supplier_profile(
        db,
        supplier_owner,
        SupplierCreate(
            business_name=payload.business_name,
            phone=payload.supplier_phone,
            address=payload.address,
        ),
    )
    supplier.approved = True
    supplier.blocked = False
    db.commit()
    db.refresh(supplier)
    logger.info("Managed supplier created supplier_id=%s user_id=%s", supplier.id, supplier_owner.id)
    return supplier


@router.get("/pending-suppliers", response_model=list[SupplierOut])
def list_pending_suppliers_endpoint(
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> list[SupplierOut]:
    return db.query(Supplier).filter(Supplier.approved.is_(False)).order_by(Supplier.id.asc()).all()


@router.post("/suppliers/{supplier_id}/approve", response_model=MessageResponse)
def approve_supplier(
    supplier_id: int,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    supplier = _get_supplier_or_404(db, supplier_id)

    supplier.approved = True
    supplier.blocked = False
    db.commit()
    logger.info("Supplier approved: supplier_id=%s", supplier_id)
    return MessageResponse(message="Supplier approved")


@router.post("/suppliers/{supplier_id}/block", response_model=MessageResponse)
def block_supplier(
    supplier_id: int,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    supplier = _get_supplier_or_404(db, supplier_id)

    supplier.blocked = True
    db.commit()
    logger.info("Supplier blocked: supplier_id=%s", supplier_id)
    return MessageResponse(message="Supplier blocked")


@router.post("/suppliers/{supplier_id}/unblock", response_model=MessageResponse)
def unblock_supplier(
    supplier_id: int,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    supplier = _get_supplier_or_404(db, supplier_id)

    supplier.blocked = False
    db.commit()
    logger.info("Supplier unblocked: supplier_id=%s", supplier_id)
    return MessageResponse(message="Supplier unblocked")


@router.delete("/suppliers/{supplier_id}", response_model=MessageResponse)
def delete_supplier(
    supplier_id: int,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    supplier = _get_supplier_or_404(db, supplier_id)

    db.delete(supplier)
    db.commit()
    logger.info("Supplier deleted: supplier_id=%s", supplier_id)
    return MessageResponse(message="Supplier deleted")


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    if user_id == current_admin.id:
        raise ConflictError("Admin cannot delete own account")

    user = _get_user_or_404(db, user_id)

    suppliers = db.query(Supplier).filter(Supplier.user_id == user.id).all()
    for supplier in suppliers:
        db.delete(supplier)

    db.delete(user)
    db.commit()
    logger.info("User deleted: user_id=%s by_admin_id=%s", user_id, current_admin.id)
    return MessageResponse(message="User deleted")


@router.post("/users/{user_id}/block", response_model=MessageResponse)
def block_user(
    user_id: int,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    if user_id == current_admin.id:
        raise ConflictError("Admin cannot block own account")
    user = _get_user_or_404(db, user_id)
    user.blocked = True
    db.commit()
    logger.info("User blocked: user_id=%s by_admin_id=%s", user_id, current_admin.id)
    return MessageResponse(message="User blocked")


@router.post("/users/{user_id}/unblock", response_model=MessageResponse)
def unblock_user(
    user_id: int,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    user = _get_user_or_404(db, user_id)
    user.blocked = False
    db.commit()
    logger.info("User unblocked: user_id=%s", user_id)
    return MessageResponse(message="User unblocked")


@router.delete("/services/{service_id}", response_model=MessageResponse)
def delete_supplier_item_by_service_id(
    service_id: int,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    delete_supplier_service(db, current_admin, service_id)
    return MessageResponse(message="Supplier item deleted")


@router.post("/categories", response_model=MessageResponse)
def create_category_endpoint(
    payload: CategoryCreate,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    key = (payload.key or "").strip().lower() or _category_key_from_name(payload.name)
    exists = db.query(Category).filter((Category.key == key) | (Category.name == payload.name)).first()
    if exists:
        raise ConflictError("Category already exists")

    db.add(Category(key=key, name=payload.name, is_enabled=payload.is_enabled))
    db.commit()
    logger.info("Category created name=%s", payload.name)
    return MessageResponse(message="Category created")


@router.get("/site-settings", response_model=SiteSettingsOut)
def get_admin_site_settings(
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> SiteSettingsOut:
    seed_site_settings(db)
    data = get_site_settings(db)
    return SiteSettingsOut(
        show_supplier_phone=data["show_supplier_phone"],
        enable_supplier_call=data["enable_supplier_call"],
        enable_supplier_whatsapp=data["enable_supplier_whatsapp"],
    )


@router.put("/site-settings", response_model=SiteSettingsOut)
def update_admin_site_settings(
    payload: SiteSettingsUpdate,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> SiteSettingsOut:
    seed_site_settings(db)
    updates: dict[str, bool] = {}
    if payload.show_supplier_phone is not None:
        updates["show_supplier_phone"] = payload.show_supplier_phone
    if payload.enable_supplier_call is not None:
        updates["enable_supplier_call"] = payload.enable_supplier_call
    if payload.enable_supplier_whatsapp is not None:
        updates["enable_supplier_whatsapp"] = payload.enable_supplier_whatsapp
    data = update_site_settings(db, updates)
    return SiteSettingsOut(
        show_supplier_phone=data["show_supplier_phone"],
        enable_supplier_call=data["enable_supplier_call"],
        enable_supplier_whatsapp=data["enable_supplier_whatsapp"],
    )


@router.get("/bookings", response_model=list[BookingOut])
def list_all_bookings_endpoint(
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> list[BookingOut]:
    return db.query(Booking).order_by(Booking.created_at.desc()).all()
