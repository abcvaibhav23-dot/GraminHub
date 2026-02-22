"""User service layer."""
from __future__ import annotations

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate


logger = logging.getLogger(__name__)
GUEST_USER_EMAIL = "guest@graminhub.local"


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise ConflictError("Email already exists")

    role = payload.role if payload.role in {"user", "supplier", "admin"} else "user"
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=role,
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

    if payload.password is not None:
        current_user.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(current_user)
    logger.info("User profile updated user_id=%s", current_user.id)
    return current_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        logger.info("Login attempt failed for unknown email=%s", email.lower())
        return None

    if not verify_password(password, user.password_hash):
        logger.info("Login attempt failed for email=%s", email.lower())
        return None

    logger.info("Login successful for email=%s", email.lower())
    return user


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
