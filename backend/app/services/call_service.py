"""Call logging service."""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.call_log import CallLog
from app.models.supplier import Supplier
from app.models.user import User
from app.services.site_setting_service import get_site_settings, seed_site_settings


logger = logging.getLogger(__name__)


def log_supplier_call(db: Session, user: User, supplier_id: int) -> tuple[CallLog, Supplier]:
    seed_site_settings(db)
    site = get_site_settings(db)
    if not site.get("enable_supplier_call", True):
        raise ForbiddenError("Supplier call is disabled by owner")

    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id, Supplier.approved.is_(True), Supplier.blocked.is_(False))
        .first()
    )
    if not supplier:
        raise NotFoundError("Supplier not found, not approved, or blocked")

    entry = CallLog(user_id=user.id, supplier_id=supplier.id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    logger.info("Supplier call logged call_id=%s user_id=%s supplier_id=%s", entry.id, user.id, supplier.id)
    return entry, supplier
