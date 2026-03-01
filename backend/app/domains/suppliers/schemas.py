"""Suppliers domain schemas (v2)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domains.suppliers.state_machine import SupplierStatus


class SupplierProfileUpsertIn(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=150)
    phone: str = Field(..., min_length=10, max_length=30)
    address: str = Field(..., min_length=3, max_length=300)


class SupplierOut(BaseModel):
    id: int
    owner_user_id: int
    business_name: str
    phone: str
    address: str
    status: SupplierStatus
    reviewer_user_id: int | None
    status_updated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class SupplierDocumentIn(BaseModel):
    doc_type: str = Field(..., min_length=2, max_length=50)
    file_url: str = Field(..., min_length=5, max_length=500)


class SupplierDocumentOut(BaseModel):
    id: int
    supplier_id: int
    doc_type: str
    file_url: str
    status: str
    reviewed_by_user_id: int | None
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
