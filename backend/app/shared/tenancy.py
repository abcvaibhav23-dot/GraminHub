"""Tenant context primitives (SaaS readiness).

v2 design: every major table is scoped by `tenant_id`, and repositories enforce tenant filtering.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str


def tenant_id_from_request(request: object, *, default: str = "default") -> str:
    headers = getattr(request, "headers", None)
    if not headers:
        return default
    raw = headers.get("X-Tenant-ID") or headers.get("x-tenant-id") or default
    value = str(raw).strip()
    return value or default
