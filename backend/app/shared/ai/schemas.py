from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


LangMode = Literal["hindi", "english"]
CategoryHint = Literal["vehicle", "materials", "coming_soon", "unknown"]


class AISearchIn(BaseModel):
    query: str = Field(..., min_length=1, max_length=320)
    language: LangMode | None = None


class AISearchOut(BaseModel):
    answer: str
    suggested_query: str | None = None
    category_hint: CategoryHint = "unknown"
    tags: list[str] = Field(default_factory=list)
    provider: Literal["openai"] = "openai"

