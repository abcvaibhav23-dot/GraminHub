"""Supplier schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict


class SupplierCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=7, max_length=30)
    address: str = Field(min_length=5, max_length=300)


class SupplierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_name: str
    phone: str
    address: str
    approved: bool
    blocked: bool
    featured: bool
    average_rating: float = 0.0
    total_reviews: int = 0


class SupplierServiceCreate(BaseModel):
    category_id: int
    price: float = Field(gt=0)
    availability: str = Field(default="available", max_length=120)


class SupplierServiceUpdate(BaseModel):
    category_id: int | None = None
    price: float | None = Field(default=None, gt=0)
    availability: str | None = Field(default=None, max_length=120)


class SupplierServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier_id: int
    category_id: int
    price: float
    availability: str


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CallResponse(BaseModel):
    supplier_id: int
    phone: str
