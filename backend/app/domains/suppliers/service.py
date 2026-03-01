"""Suppliers domain services (v2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.domains.suppliers.models import V2Supplier, V2SupplierDocument
from app.domains.suppliers.policies import can_approve_supplier, can_create_supplier_profile, can_submit_supplier_docs
from app.domains.suppliers.repository import SupplierRepository
from app.domains.suppliers.state_machine import SupplierAction, SupplierStatus, transition
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.shared.policies import Actor


class SupplierService:
    def __init__(self, db: Session, *, actor: Actor):
        self._db = db
        self._actor = actor
        self._repo = SupplierRepository(db, tenant_id=actor.tenant_id)

    def upsert_my_profile(self, *, business_name: str, phone: str, address: str) -> V2Supplier:
        if not can_create_supplier_profile(self._actor):
            raise ForbiddenError("Not allowed to create supplier profile")

        existing = self._repo.get_by_owner(self._actor.user_id)
        if existing:
            existing.business_name = business_name
            existing.phone = phone
            existing.address = address
            existing.status_updated_at = datetime.utcnow()
            return self._repo.upsert_profile(existing)

        supplier = V2Supplier(
            tenant_id=self._actor.tenant_id,
            owner_user_id=self._actor.user_id,
            business_name=business_name,
            phone=phone,
            address=address,
            status=SupplierStatus.REGISTERED.value,
            reviewer_user_id=None,
            status_updated_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        return self._repo.upsert_profile(supplier)

    def my_profile(self) -> V2Supplier:
        supplier = self._repo.get_by_owner(self._actor.user_id)
        if not supplier:
            raise NotFoundError("Supplier profile not found")
        return supplier

    def submit_document(self, *, doc_type: str, file_url: str) -> V2SupplierDocument:
        if not can_submit_supplier_docs(self._actor):
            raise ForbiddenError("Not allowed to submit documents")
        supplier = self._repo.get_by_owner(self._actor.user_id)
        if not supplier:
            raise NotFoundError("Supplier profile not found")

        doc = V2SupplierDocument(
            tenant_id=self._actor.tenant_id,
            supplier_id=supplier.id,
            doc_type=doc_type,
            file_url=file_url,
            status="SUBMITTED",
            reviewed_by_user_id=None,
            reviewed_at=None,
            created_at=datetime.utcnow(),
        )
        doc = self._repo.add_document(doc)

        # Lifecycle update: REGISTERED -> DOCUMENT_SUBMITTED (first doc submission).
        current = SupplierStatus(supplier.status)
        if current == SupplierStatus.REGISTERED:
            supplier.status = transition(current, SupplierAction.SUBMIT_DOCUMENTS).value
            supplier.status_updated_at = datetime.utcnow()
            self._repo.upsert_profile(supplier)

        return doc

    def list_my_documents(self) -> list[V2SupplierDocument]:
        supplier = self._repo.get_by_owner(self._actor.user_id)
        if not supplier:
            raise NotFoundError("Supplier profile not found")
        return self._repo.list_documents(supplier.id)

    def admin_verify(self, *, supplier_id: int) -> V2Supplier:
        if not can_approve_supplier(self._actor):
            raise ForbiddenError("Not allowed to verify suppliers")
        supplier = self._repo.get(supplier_id)
        if not supplier:
            raise NotFoundError("Supplier not found")

        current = SupplierStatus(supplier.status)
        if current == SupplierStatus.DOCUMENT_SUBMITTED:
            supplier.status = transition(current, SupplierAction.START_REVIEW).value
            supplier.reviewer_user_id = self._actor.user_id
            supplier.status_updated_at = datetime.utcnow()
            supplier = self._repo.upsert_profile(supplier)
            current = SupplierStatus(supplier.status)

        try:
            supplier.status = transition(current, SupplierAction.VERIFY).value
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        supplier.reviewer_user_id = self._actor.user_id
        supplier.status_updated_at = datetime.utcnow()
        return self._repo.upsert_profile(supplier)

    def admin_reject(self, *, supplier_id: int) -> V2Supplier:
        if not can_approve_supplier(self._actor):
            raise ForbiddenError("Not allowed to reject suppliers")
        supplier = self._repo.get(supplier_id)
        if not supplier:
            raise NotFoundError("Supplier not found")
        current = SupplierStatus(supplier.status)
        try:
            supplier.status = transition(current, SupplierAction.REJECT).value
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        supplier.reviewer_user_id = self._actor.user_id
        supplier.status_updated_at = datetime.utcnow()
        return self._repo.upsert_profile(supplier)
