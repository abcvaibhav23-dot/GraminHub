"""Supplier schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict


class SupplierCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=7, max_length=30)
    address: str = Field(min_length=5, max_length=300)


class SupplierServiceCreate(BaseModel):
    category_id: int | None = None
    item_name: str = Field(min_length=2, max_length=160)
    item_details: str | None = Field(default=None, max_length=500)
    item_variant: str | None = Field(default=None, max_length=160)
    photo_url_1: str | None = Field(default=None, max_length=500)
    photo_url_2: str | None = Field(default=None, max_length=500)
    photo_url_3: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)
    price_unit_type: str = Field(default="per_item", max_length=40)
    availability: str = Field(default="available", max_length=120)


class SupplierServiceUpdate(BaseModel):
    category_id: int | None = None
    item_name: str | None = Field(default=None, max_length=160)
    item_details: str | None = Field(default=None, max_length=500)
    item_variant: str | None = Field(default=None, max_length=160)
    photo_url_1: str | None = Field(default=None, max_length=500)
    photo_url_2: str | None = Field(default=None, max_length=500)
    photo_url_3: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)
    price_unit_type: str | None = Field(default=None, max_length=40)
    availability: str | None = Field(default=None, max_length=120)


class SupplierServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier_id: int
    category_id: int | None = None
    item_name: str | None = None
    item_details: str | None = None
    item_variant: str | None = None
    photo_url_1: str | None = None
    photo_url_2: str | None = None
    photo_url_3: str | None = None
    price: float | None = None
    price_unit_type: str
    availability: str


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
    services: list[SupplierServiceOut] = Field(default_factory=list)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    name: str
    is_enabled: bool


class CallResponse(BaseModel):
    supplier_id: int
    phone: str
