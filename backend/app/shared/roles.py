"""Role primitives used across v2 domains."""
from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    SUPPLIER = "SUPPLIER"
    BUYER = "BUYER"


def role_from_v1(role: str | None) -> Role:
    normalized = (role or "").strip().lower()
    if normalized == "admin":
        return Role.ADMIN
    if normalized == "supplier":
        return Role.SUPPLIER
    return Role.BUYER

