"""Supplier and supplier service models."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    business_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="suppliers")
    services = relationship("SupplierService", back_populates="supplier", cascade="all, delete-orphan")


class SupplierService(Base):
    __tablename__ = "supplier_services"
    __table_args__ = (
        Index("ix_supplier_services_supplier_id", "supplier_id"),
        Index("ix_supplier_services_category_id", "category_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    availability: Mapped[str] = mapped_column(String(120), nullable=False, default="available")

    supplier = relationship("Supplier", back_populates="services")
    category = relationship("Category", back_populates="services")
