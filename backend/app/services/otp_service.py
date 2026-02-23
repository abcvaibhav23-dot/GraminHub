"""Secure OTP challenge lifecycle."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import TooManyRequestsError, UnauthorizedError
from app.models.otp_challenge import OtpChallenge


def _otp_hash_pepper() -> str:
    return settings.OTP_HASH_PEPPER or settings.JWT_SECRET_KEY


def _utcnow() -> datetime:
    return datetime.utcnow()


def _otp_digest(*, phone: str, role: str, otp_code: str, nonce: str) -> str:
    payload = f"{phone}:{role}:{otp_code}:{nonce}".encode("utf-8")
    return hmac.new(_otp_hash_pepper().encode("utf-8"), payload, hashlib.sha256).hexdigest()


def generate_otp_code() -> str:
    upper = 10 ** settings.OTP_CODE_LENGTH
    return f"{secrets.randbelow(upper):0{settings.OTP_CODE_LENGTH}d}"


def _mark_active_challenges_consumed(db: Session, *, phone: str, role: str, now: datetime) -> None:
    (
        db.query(OtpChallenge)
        .filter(
            OtpChallenge.phone == phone,
            OtpChallenge.role == role,
            OtpChallenge.consumed_at.is_(None),
        )
        .update({OtpChallenge.consumed_at: now}, synchronize_session=False)
    )


def _cleanup_old_challenges(db: Session, *, now: datetime) -> None:
    retention_cutoff = now - timedelta(days=2)
    (
        db.query(OtpChallenge)
        .filter(
            OtpChallenge.created_at < retention_cutoff,
        )
        .delete(synchronize_session=False)
    )


def create_otp_challenge(
    db: Session,
    *,
    phone: str,
    role: str,
    requested_ip: str | None = None,
) -> tuple[OtpChallenge, str]:
    now = _utcnow()
    _cleanup_old_challenges(db, now=now)

    latest_active = (
        db.query(OtpChallenge)
        .filter(
            OtpChallenge.phone == phone,
            OtpChallenge.role == role,
            OtpChallenge.consumed_at.is_(None),
        )
        .order_by(OtpChallenge.created_at.desc())
        .first()
    )
    if latest_active:
        elapsed = (now - latest_active.created_at).total_seconds()
        if elapsed < settings.OTP_RESEND_INTERVAL_SECONDS:
            retry_after = int(settings.OTP_RESEND_INTERVAL_SECONDS - elapsed)
            raise TooManyRequestsError(
                f"OTP recently requested. Retry after {max(retry_after, 1)} seconds"
            )

    _mark_active_challenges_consumed(db, phone=phone, role=role, now=now)

    otp_code = generate_otp_code()
    nonce = secrets.token_hex(16)
    challenge = OtpChallenge(
        phone=phone,
        role=role,
        code_hash=_otp_digest(phone=phone, role=role, otp_code=otp_code, nonce=nonce),
        nonce=nonce,
        expires_at=now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        max_attempts=settings.OTP_MAX_VERIFY_ATTEMPTS,
        attempt_count=0,
        created_at=now,
        requested_ip=requested_ip,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge, otp_code


def invalidate_otp_challenge(db: Session, *, challenge_id: int) -> None:
    challenge = db.query(OtpChallenge).filter(OtpChallenge.id == challenge_id).first()
    if not challenge or challenge.consumed_at is not None:
        return
    challenge.consumed_at = _utcnow()
    db.commit()


def verify_otp_challenge(db: Session, *, phone: str, role: str, otp_code: str) -> None:
    now = _utcnow()
    challenge = (
        db.query(OtpChallenge)
        .filter(
            OtpChallenge.phone == phone,
            OtpChallenge.role == role,
            OtpChallenge.consumed_at.is_(None),
        )
        .order_by(OtpChallenge.created_at.desc())
        .first()
    )
    if not challenge:
        raise UnauthorizedError("OTP not requested")

    if now > challenge.expires_at:
        challenge.consumed_at = now
        db.commit()
        raise UnauthorizedError("OTP expired")

    if challenge.attempt_count >= challenge.max_attempts:
        challenge.consumed_at = now
        db.commit()
        raise TooManyRequestsError("Too many invalid OTP attempts. Request a new OTP.")

    expected = _otp_digest(
        phone=challenge.phone,
        role=challenge.role,
        otp_code=otp_code,
        nonce=challenge.nonce,
    )
    if not hmac.compare_digest(expected, challenge.code_hash):
        challenge.attempt_count += 1
        challenge.last_attempt_at = now
        if challenge.attempt_count >= challenge.max_attempts:
            challenge.consumed_at = now
            db.commit()
            raise TooManyRequestsError("Too many invalid OTP attempts. Request a new OTP.")
        db.commit()
        raise UnauthorizedError("Invalid OTP")

    challenge.last_attempt_at = now
    challenge.consumed_at = now
    db.commit()
