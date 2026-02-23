"""User service layer."""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate


logger = logging.getLogger(__name__)
GUEST_USER_EMAIL = "guest@graminhub.local"
OTP_ROLE_PREFIX = "otp"
OTP_LOGIN_ROLES = {"user", "supplier", "admin"}


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise ConflictError("Email already exists")

    if payload.role == "admin":
        raise ForbiddenError("Admin registration is restricted")

    role = payload.role if payload.role in {"user", "supplier"} else "user"
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        phone=normalize_phone(payload.phone) if payload.phone else None,
        password_hash=hash_password(payload.password),
        role=role,
        blocked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("User created user_id=%s role=%s", user.id, user.role)
    return user


def update_user_profile(db: Session, current_user: User, payload: UserUpdate) -> User:
    if payload.name is not None:
        current_user.name = payload.name

    if payload.email is not None:
        email = payload.email.lower()
        existing = db.query(User).filter(User.email == email, User.id != current_user.id).first()
        if existing:
            raise ConflictError("Email already exists")
        current_user.email = email

    if payload.phone is not None:
        current_user.phone = normalize_phone(payload.phone)

    if payload.password is not None:
        current_user.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(current_user)
    logger.info("User profile updated user_id=%s", current_user.id)
    return current_user


def get_or_create_guest_user(db: Session) -> User:
    user = db.query(User).filter(User.email == GUEST_USER_EMAIL).first()
    if user:
        return user

    user = User(
        name="Guest Booking User",
        email=GUEST_USER_EMAIL,
        password_hash=hash_password("guest-booking-internal"),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Created internal guest booking user user_id=%s", user.id)
    return user


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(digits) == 10:
        return f"91{digits}"
    return digits


def otp_email_for_phone_role(phone: str, role: str) -> str:
    normalized_phone = normalize_phone(phone)
    normalized_role = (role or "").strip().lower()
    safe_role = normalized_role if normalized_role in OTP_LOGIN_ROLES else "user"
    return f"{OTP_ROLE_PREFIX}.{safe_role}.{normalized_phone}@graminhub.local"


def get_or_create_phone_role_user(
    db: Session,
    *,
    phone: str,
    role: str,
    name: str | None = None,
) -> User:
    normalized_role = (role or "").strip().lower()
    safe_role = normalized_role if normalized_role in OTP_LOGIN_ROLES else "user"
    normalized_phone = normalize_phone(phone)

    # Prefer exact phone+role match to avoid creating duplicate identities.
    user = (
        db.query(User)
        .filter(
            User.phone == normalized_phone,
            User.role == safe_role,
        )
        .order_by(User.id.asc())
        .first()
    )
    if user:
        if name and name.strip():
            user.name = name.strip()
            db.commit()
            db.refresh(user)
        return user

    email = otp_email_for_phone_role(phone, safe_role)
    user = db.query(User).filter(User.email == email, User.role == safe_role).first()
    if user:
        if not user.phone:
            user.phone = normalized_phone
            db.commit()
            db.refresh(user)
        if name and name.strip():
            user.name = name.strip()
            db.commit()
            db.refresh(user)
        return user

    display_name = (name or "").strip() or f"{safe_role.title()} {normalized_phone[-4:]}"
    user = User(
        name=display_name,
        email=email,
        phone=normalized_phone,
        password_hash=hash_password(f"otp-{normalized_phone}-{safe_role}"),
        role=safe_role,
        blocked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("OTP user auto-created user_id=%s role=%s phone=%s", user.id, safe_role, normalized_phone)
    return user
