"""Authentication routes."""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.security import create_access_token
from app.schemas.user_schema import LoginRequest, TokenResponse, UserCreate, UserOut
from app.services.user_service import authenticate_user, create_user


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    return create_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login_user_endpoint(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        logger.info("Login failed email=%s", payload.email.lower())
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id), role=user.role)
    logger.info("Login success user_id=%s", user.id)
    return TokenResponse(access_token=token)
