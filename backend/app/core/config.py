"""App settings and database setup."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "GraminHub")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "0") == "1"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:////tmp/graminhub.db",
    )
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-env")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    OTP_CODE_LENGTH: int = int(os.getenv("OTP_CODE_LENGTH", "6"))
    OTP_EXPIRY_MINUTES: int = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))
    OTP_MAX_VERIFY_ATTEMPTS: int = int(os.getenv("OTP_MAX_VERIFY_ATTEMPTS", "5"))
    OTP_RESEND_INTERVAL_SECONDS: int = int(os.getenv("OTP_RESEND_INTERVAL_SECONDS", "30"))
    OTP_EXPOSE_IN_RESPONSE: bool = os.getenv(
        "OTP_EXPOSE_IN_RESPONSE",
        "0" if os.getenv("APP_ENV", "development").lower() == "production" else "1",
    ) == "1"
    OTP_DELIVERY_MODE: str = os.getenv(
        "OTP_DELIVERY_MODE",
        "console" if os.getenv("APP_ENV", "development").lower() != "production" else "webhook",
    ).strip().lower()
    OTP_WEBHOOK_URL: str = os.getenv("OTP_WEBHOOK_URL", "").strip()
    OTP_WEBHOOK_TOKEN: str = os.getenv("OTP_WEBHOOK_TOKEN", "").strip()
    OTP_HASH_PEPPER: str = os.getenv("OTP_HASH_PEPPER", "").strip()
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8000,https://graminhub.in,https://www.graminhub.in",
    )
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
    ADMIN_PHONE_ALLOWLIST: str = os.getenv("ADMIN_PHONE_ALLOWLIST", "9000000001")

    PUBLIC_SUPPORT_EMAIL: str = os.getenv("PUBLIC_SUPPORT_EMAIL", "support@example.com").strip()
    PUBLIC_SUPPORT_PHONE: str = os.getenv("PUBLIC_SUPPORT_PHONE", "+91-9000000000").strip()
    PUBLIC_SUPPORT_WHATSAPP: str = os.getenv("PUBLIC_SUPPORT_WHATSAPP", "+91-9000000000").strip()


settings = Settings()

if settings.OTP_CODE_LENGTH < 4 or settings.OTP_CODE_LENGTH > 8:
    raise RuntimeError("OTP_CODE_LENGTH must be between 4 and 8")
if settings.OTP_EXPIRY_MINUTES < 1 or settings.OTP_EXPIRY_MINUTES > 15:
    raise RuntimeError("OTP_EXPIRY_MINUTES must be between 1 and 15")
if settings.OTP_MAX_VERIFY_ATTEMPTS < 1 or settings.OTP_MAX_VERIFY_ATTEMPTS > 10:
    raise RuntimeError("OTP_MAX_VERIFY_ATTEMPTS must be between 1 and 10")
if settings.OTP_RESEND_INTERVAL_SECONDS < 0 or settings.OTP_RESEND_INTERVAL_SECONDS > 300:
    raise RuntimeError("OTP_RESEND_INTERVAL_SECONDS must be between 0 and 300")

if settings.APP_ENV.lower() == "production":
    insecure_secrets = {
        "change-me-in-env",
        "replace-with-long-random-secret",
        "",
    }
    if settings.JWT_SECRET_KEY in insecure_secrets:
        raise RuntimeError("JWT_SECRET_KEY must be set to a strong value in production")
    if settings.OTP_EXPOSE_IN_RESPONSE:
        raise RuntimeError("OTP_EXPOSE_IN_RESPONSE must be disabled in production")
    if settings.OTP_DELIVERY_MODE == "console":
        raise RuntimeError("OTP_DELIVERY_MODE=console is not allowed in production")
    if settings.OTP_DELIVERY_MODE == "webhook" and not settings.OTP_WEBHOOK_URL:
        raise RuntimeError("OTP_WEBHOOK_URL is required for OTP webhook delivery in production")

_default_log_dir = BASE_DIR / "logs"
try:
    _default_log_dir.mkdir(parents=True, exist_ok=True)
    LOG_DIR = _default_log_dir
except OSError:
    LOG_DIR = Path("/tmp/graminhub-logs")
    LOG_DIR.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
