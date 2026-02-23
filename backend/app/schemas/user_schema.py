"""User/auth schemas."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    password: str = Field(min_length=6, max_length=128)
    role: str = Field(default="user")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str | None = None
    role: str
    blocked: bool = False
    created_at: datetime


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    email: str | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    password: str | None = Field(default=None, min_length=6, max_length=128)


class PhoneOtpRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)
    role: str = Field(default="user")
    name: str | None = Field(default=None, min_length=2, max_length=120)


class PhoneOtpVerify(BaseModel):
    phone: str = Field(min_length=7, max_length=20)
    otp: str = Field(min_length=2, max_length=6)
    role: str = Field(default="user")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
