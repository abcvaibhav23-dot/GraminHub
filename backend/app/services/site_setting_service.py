"""Site settings service layer."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.site_setting import SiteSetting


DEFAULT_BOOL: dict[str, bool] = {
    "show_supplier_phone": True,
    "enable_supplier_call": True,
    "enable_supplier_whatsapp": True,
}

DEFAULT_STR: dict[str, str] = {
    "public_support_email": settings.PUBLIC_SUPPORT_EMAIL,
    "public_support_phone": settings.PUBLIC_SUPPORT_PHONE,
    "public_support_whatsapp": settings.PUBLIC_SUPPORT_WHATSAPP,
}


def seed_site_settings(db: Session) -> None:
    now = datetime.utcnow()
    for key, value in DEFAULT_BOOL.items():
        exists = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if exists:
            continue
        db.add(SiteSetting(key=key, bool_value=bool(value), updated_at=now))

    for key, value in DEFAULT_STR.items():
        exists = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if exists:
            if key in DEFAULT_STR and (exists.str_value is None or not str(exists.str_value).strip()):
                exists.str_value = str(value).strip()
                exists.updated_at = now
            continue
        db.add(SiteSetting(key=key, bool_value=True, str_value=str(value).strip(), updated_at=now))
    db.commit()


def get_site_settings(db: Session) -> dict[str, object]:
    rows = db.query(SiteSetting).all()
    out: dict[str, object] = {**DEFAULT_BOOL, **DEFAULT_STR}
    for row in rows:
        if row.key in DEFAULT_BOOL:
            out[row.key] = bool(row.bool_value)
        elif row.key in DEFAULT_STR:
            out[row.key] = (row.str_value or DEFAULT_STR[row.key]).strip()
    return out


def update_site_settings(db: Session, updates: dict[str, object]) -> dict[str, object]:
    now = datetime.utcnow()
    for key, value in updates.items():
        if key not in DEFAULT_BOOL and key not in DEFAULT_STR:
            continue
        row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if not row:
            row = SiteSetting(key=key, bool_value=True, updated_at=now)
            db.add(row)
        if key in DEFAULT_BOOL:
            row.bool_value = bool(value)
        if key in DEFAULT_STR:
            row.str_value = str(value).strip()
        row.updated_at = now
    db.commit()
    return get_site_settings(db)
