"""Central policy helpers (v2).

Routes must not contain permission logic. They should call policies from services.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.shared.roles import Role, role_from_v1


@dataclass(frozen=True)
class Actor:
    user_id: int
    role: Role
    tenant_id: str = "default"

    @staticmethod
    def from_v1_user(user: object, *, tenant_id: str = "default") -> "Actor":
        user_id = int(getattr(user, "id"))
        role = role_from_v1(getattr(user, "role", None))
        return Actor(user_id=user_id, role=role, tenant_id=tenant_id)


def is_admin(actor: Actor) -> bool:
    return actor.role in {Role.ADMIN, Role.SUPER_ADMIN}


def can_view_dashboard(actor: Actor) -> bool:
    return is_admin(actor) or actor.role == Role.SUPPLIER

