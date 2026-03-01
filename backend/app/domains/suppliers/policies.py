"""Suppliers domain policies (v2)."""

from __future__ import annotations

from app.shared.policies import Actor, is_admin
from app.shared.roles import Role


def can_create_supplier_profile(actor: Actor) -> bool:
    return actor.role in {Role.SUPPLIER, Role.ADMIN, Role.SUPER_ADMIN}


def can_submit_supplier_docs(actor: Actor) -> bool:
    return actor.role == Role.SUPPLIER


def can_approve_supplier(actor: Actor) -> bool:
    return is_admin(actor)

