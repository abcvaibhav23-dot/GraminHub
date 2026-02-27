"""Site settings service layer."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.site_setting import SiteSetting


DEFAULTS: dict[str, bool] = {
    "show_supplier_phone": True,
    "enable_supplier_call": True,
    "enable_supplier_whatsapp": True,
}


def seed_site_settings(db: Session) -> None:
    for key, value in DEFAULTS.items():
        exists = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if exists:
            continue
        db.add(SiteSetting(key=key, bool_value=bool(value), updated_at=datetime.utcnow()))
    db.commit()


def get_site_settings(db: Session) -> dict[str, bool]:
    rows = db.query(SiteSetting).all()
    out = {**DEFAULTS}
    for row in rows:
        out[row.key] = bool(row.bool_value)
    return out


def update_site_settings(db: Session, updates: dict[str, bool]) -> dict[str, bool]:
    now = datetime.utcnow()
    for key, value in updates.items():
        if key not in DEFAULTS:
            continue
        row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if not row:
            row = SiteSetting(key=key, bool_value=bool(value), updated_at=now)
            db.add(row)
        else:
            row.bool_value = bool(value)
            row.updated_at = now
    db.commit()
    return get_site_settings(db)

