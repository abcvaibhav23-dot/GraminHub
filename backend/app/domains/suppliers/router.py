"""Suppliers domain router (v2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.security import get_current_user
from app.domains.suppliers.schemas import (
    SupplierDocumentIn,
    SupplierDocumentOut,
    SupplierOut,
    SupplierProfileUpsertIn,
)
from app.domains.suppliers.service import SupplierService
from app.shared.policies import Actor
from app.shared.tenancy import tenant_id_from_request


router = APIRouter(prefix="/api/v2/suppliers", tags=["v2-suppliers"])


def _service(request: Request, db: Session, current_user: object) -> SupplierService:
    tenant_id = tenant_id_from_request(request)
    actor = Actor.from_v1_user(current_user, tenant_id=tenant_id)
    return SupplierService(db, actor=actor)


@router.post("/profile", response_model=SupplierOut)
def upsert_profile(
    payload: SupplierProfileUpsertIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> SupplierOut:
    service = _service(request, db, current_user)
    return service.upsert_my_profile(
        business_name=payload.business_name,
        phone=payload.phone,
        address=payload.address,
    )


@router.get("/me", response_model=SupplierOut)
def my_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> SupplierOut:
    service = _service(request, db, current_user)
    return service.my_profile()


@router.post("/me/documents", response_model=SupplierDocumentOut)
def submit_document(
    payload: SupplierDocumentIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> SupplierDocumentOut:
    service = _service(request, db, current_user)
    return service.submit_document(doc_type=payload.doc_type, file_url=payload.file_url)


@router.get("/me/documents", response_model=list[SupplierDocumentOut])
def list_my_docs(
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> list[SupplierDocumentOut]:
    service = _service(request, db, current_user)
    return service.list_my_documents()


@router.post("/{supplier_id}/verify", response_model=SupplierOut)
def admin_verify_supplier(
    supplier_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> SupplierOut:
    service = _service(request, db, current_user)
    return service.admin_verify(supplier_id=supplier_id)


@router.post("/{supplier_id}/reject", response_model=SupplierOut)
def admin_reject_supplier(
    supplier_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> SupplierOut:
    service = _service(request, db, current_user)
    return service.admin_reject(supplier_id=supplier_id)
