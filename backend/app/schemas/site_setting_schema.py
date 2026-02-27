"""Site settings schemas."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SiteSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    show_supplier_phone: bool
    enable_supplier_call: bool
    enable_supplier_whatsapp: bool


class SiteSettingsUpdate(BaseModel):
    show_supplier_phone: bool | None = None
    enable_supplier_call: bool | None = None
    enable_supplier_whatsapp: bool | None = None

