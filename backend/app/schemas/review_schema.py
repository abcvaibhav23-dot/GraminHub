"""Review schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    supplier_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=2, max_length=500)


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    supplier_id: int
    rating: int
    comment: str
