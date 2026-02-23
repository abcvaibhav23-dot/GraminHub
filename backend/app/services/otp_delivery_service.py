"""OTP delivery integrations."""
from __future__ import annotations

import logging

import httpx

from app.core.config import settings
from app.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


def send_otp(*, phone: str, role: str, otp_code: str) -> None:
    mode = settings.OTP_DELIVERY_MODE
    if mode == "console":
        logger.info("OTP delivery console mode role=%s phone=%s otp=%s", role, phone, otp_code)
        return

    if mode == "webhook":
        if not settings.OTP_WEBHOOK_URL:
            raise ValidationError("OTP webhook URL is not configured")
        headers = {"Content-Type": "application/json"}
        if settings.OTP_WEBHOOK_TOKEN:
            headers["Authorization"] = f"Bearer {settings.OTP_WEBHOOK_TOKEN}"

        payload = {"phone": phone, "role": role, "otp": otp_code}
        try:
            response = httpx.post(
                settings.OTP_WEBHOOK_URL,
                json=payload,
                headers=headers,
                timeout=8.0,
            )
        except httpx.HTTPError as exc:
            logger.warning("OTP webhook request failed role=%s phone=%s error=%s", role, phone, str(exc))
            raise ValidationError("OTP delivery failed") from exc

        if response.status_code >= 400:
            logger.warning(
                "OTP webhook non-success role=%s phone=%s status=%s body=%s",
                role,
                phone,
                response.status_code,
                response.text[:200],
            )
            raise ValidationError("OTP delivery failed")
        return

    raise ValidationError("Unsupported OTP_DELIVERY_MODE")
