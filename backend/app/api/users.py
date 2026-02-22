"""User routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user_schema import UserOut, UserUpdate
from app.services.user_service import update_user_profile


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_my_profile_endpoint(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user


@router.put("/me", response_model=UserOut)
def update_my_profile_endpoint(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    return update_user_profile(db, current_user, payload)


@router.post("/me/update", response_model=UserOut)
def update_my_profile_legacy_endpoint(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    return update_user_profile(db, current_user, payload)
