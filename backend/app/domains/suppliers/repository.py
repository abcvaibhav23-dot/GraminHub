"""Suppliers domain repository (v2)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domains.suppliers.models import V2Supplier, V2SupplierDocument


class SupplierRepository:
    def __init__(self, db: Session, *, tenant_id: str):
        self._db = db
        self._tenant_id = tenant_id

    def get(self, supplier_id: int) -> V2Supplier | None:
        return (
            self._db.query(V2Supplier)
            .filter(V2Supplier.tenant_id == self._tenant_id, V2Supplier.id == supplier_id)
            .first()
        )

    def get_by_owner(self, owner_user_id: int) -> V2Supplier | None:
        return (
            self._db.query(V2Supplier)
            .filter(V2Supplier.tenant_id == self._tenant_id, V2Supplier.owner_user_id == owner_user_id)
            .order_by(V2Supplier.id.asc())
            .first()
        )

    def upsert_profile(self, supplier: V2Supplier) -> V2Supplier:
        self._db.add(supplier)
        self._db.commit()
        self._db.refresh(supplier)
        return supplier

    def add_document(self, doc: V2SupplierDocument) -> V2SupplierDocument:
        self._db.add(doc)
        self._db.commit()
        self._db.refresh(doc)
        return doc

    def list_documents(self, supplier_id: int) -> list[V2SupplierDocument]:
        return (
            self._db.query(V2SupplierDocument)
            .filter(
                V2SupplierDocument.tenant_id == self._tenant_id,
                V2SupplierDocument.supplier_id == supplier_id,
            )
            .order_by(V2SupplierDocument.created_at.desc())
            .all()
        )
