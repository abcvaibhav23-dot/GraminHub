"""Public settings endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.schemas.site_setting_schema import SiteSettingsOut
from app.services.site_setting_service import get_site_settings, seed_site_settings


router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/site-settings", response_model=SiteSettingsOut)
def get_public_site_settings(db: Session = Depends(get_db)) -> SiteSettingsOut:
    seed_site_settings(db)
    data = get_site_settings(db)
    return SiteSettingsOut(
        show_supplier_phone=data["show_supplier_phone"],
        enable_supplier_call=data["enable_supplier_call"],
        enable_supplier_whatsapp=data["enable_supplier_whatsapp"],
        public_support_email=str(data.get("public_support_email") or ""),
        public_support_phone=str(data.get("public_support_phone") or ""),
        public_support_whatsapp=str(data.get("public_support_whatsapp") or ""),
    )
