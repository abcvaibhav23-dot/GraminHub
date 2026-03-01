"""Suppliers domain models (v2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db import Base
from app.domains.suppliers.state_machine import SupplierStatus


class V2Supplier(Base):
    __tablename__ = "v2_suppliers"
    __table_args__ = (
        Index("ix_v2_suppliers_tenant_owner", "tenant_id", "owner_user_id"),
        Index("ix_v2_suppliers_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    owner_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    business_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)

    status: Mapped[str] = mapped_column(String(40), nullable=False, default=SupplierStatus.REGISTERED.value)
    reviewer_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    documents = relationship("V2SupplierDocument", back_populates="supplier", cascade="all, delete-orphan")


class V2SupplierDocument(Base):
    __tablename__ = "v2_supplier_documents"
    __table_args__ = (
        Index("ix_v2_supplier_documents_tenant_supplier", "tenant_id", "supplier_id"),
        Index("ix_v2_supplier_documents_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("v2_suppliers.id", ondelete="CASCADE"), nullable=False)

    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="SUBMITTED")
    reviewed_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    supplier = relationship("V2Supplier", back_populates="documents")
