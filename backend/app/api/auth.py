"""Authentication routes."""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import get_db, settings
from app.core.security import create_access_token
from app.core.exceptions import ServiceError
from app.schemas.user_schema import (
    PhoneOtpRequest,
    PhoneOtpVerify,
    TokenResponse,
    UserCreate,
    UserOut,
)
from app.services.user_service import (
    create_user,
    get_or_create_phone_role_user,
    normalize_phone,
)
from app.services.otp_service import create_otp_challenge, invalidate_otp_challenge, verify_otp_challenge
from app.services.otp_delivery_service import send_otp


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


def _validate_phone_for_otp(phone: str) -> str:
    normalized_phone = normalize_phone(phone)
    if len(normalized_phone) < 10 or len(normalized_phone) > 14:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    return normalized_phone


def _validate_otp_role(role: str) -> str:
    normalized_role = (role or "").strip().lower()
    safe_role = normalized_role if normalized_role in {"user", "supplier", "admin"} else "user"
    return safe_role


def _admin_phone_allowlist() -> set[str]:
    return {
        normalize_phone(raw_phone)
        for raw_phone in settings.ADMIN_PHONE_ALLOWLIST.split(",")
        if raw_phone.strip()
    }


def _ensure_admin_phone_allowed(role: str, normalized_phone: str) -> None:
    if role != "admin":
        return
    if normalized_phone not in _admin_phone_allowlist():
        logger.warning("Blocked admin OTP for non-allowlisted phone=%s", normalized_phone)
        raise HTTPException(status_code=403, detail="Admin access is not allowed for this phone")


@router.post("/register", response_model=UserOut)
def register_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    return create_user(db, payload)


@router.post("/otp/request")
def request_phone_otp_endpoint(
    payload: PhoneOtpRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    normalized_phone = _validate_phone_for_otp(payload.phone)
    safe_role = _validate_otp_role(payload.role)
    _ensure_admin_phone_allowed(safe_role, normalized_phone)

    # Ensure account exists for selected role without requiring email login.
    managed_user = get_or_create_phone_role_user(
        db,
        phone=normalized_phone,
        role=safe_role,
        name=payload.name,
    )
    if managed_user.blocked:
        raise HTTPException(status_code=403, detail="Account is blocked by admin")

    request_ip = request.client.host if request.client else None

    try:
        challenge, otp_code = create_otp_challenge(
            db,
            phone=normalized_phone,
            role=safe_role,
            requested_ip=request_ip,
        )
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    try:
        send_otp(phone=normalized_phone, role=safe_role, otp_code=otp_code)
    except ServiceError as exc:
        invalidate_otp_challenge(db, challenge_id=challenge.id)
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    logger.info(
        "OTP issued role=%s phone=%s expires_at=%s challenge_id=%s",
        safe_role,
        normalized_phone,
        challenge.expires_at.isoformat(),
        challenge.id,
    )

    response = {
        "message": "OTP issued",
        "expires_in_seconds": settings.OTP_EXPIRY_MINUTES * 60,
        "role": safe_role,
        "phone": normalized_phone,
    }
    # Only expose OTP in non-production/demo environments.
    if settings.OTP_EXPOSE_IN_RESPONSE:
        response["otp"] = otp_code
    return response


@router.post("/otp/verify", response_model=TokenResponse)
def verify_phone_otp_endpoint(payload: PhoneOtpVerify, db: Session = Depends(get_db)) -> TokenResponse:
    normalized_phone = _validate_phone_for_otp(payload.phone)
    safe_role = _validate_otp_role(payload.role)
    _ensure_admin_phone_allowed(safe_role, normalized_phone)
    otp_code = (payload.otp or "").strip()
    if not otp_code.isdigit() or len(otp_code) != settings.OTP_CODE_LENGTH:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    try:
        verify_otp_challenge(db, phone=normalized_phone, role=safe_role, otp_code=otp_code)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    user = get_or_create_phone_role_user(db, phone=normalized_phone, role=safe_role)
    if user.blocked:
        raise HTTPException(status_code=403, detail="Account is blocked by admin")
    token = create_access_token(subject=str(user.id), role=user.role)
    logger.info("OTP login success user_id=%s role=%s phone=%s", user.id, user.role, normalized_phone)
    return TokenResponse(access_token=token)
