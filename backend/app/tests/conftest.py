from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_FILE = Path("/tmp/marketplace_test.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("ADMIN_PHONE_ALLOWLIST", "9000000001")

from app.core.config import Base, get_db
from app.main import app, rate_buckets
from app.services.supplier_service import seed_default_categories

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    if TEST_DB_FILE.exists():
        TEST_DB_FILE.unlink()
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_default_categories(db)
    db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    if TEST_DB_FILE.exists():
        TEST_DB_FILE.unlink()


@pytest.fixture
def client():
    rate_buckets.clear()
    with TestClient(app) as c:
        yield c


def phone_for_identity(*, role: str, email: str) -> str:
    digest = hashlib.sha1(f"{role}:{email}".encode()).hexdigest()
    ten_digits = str(int(digest[:12], 16)).zfill(10)[-10:]
    return f"9{ten_digits[1:]}"


def otp_login(client: TestClient, *, phone: str, role: str, name: str | None = None) -> str:
    otp_req = client.post("/api/auth/otp/request", json={"phone": phone, "role": role, "name": name})
    assert otp_req.status_code == 200, otp_req.text
    otp_code = otp_req.json()["otp"]

    token_resp = client.post("/api/auth/otp/verify", json={"phone": phone, "role": role, "otp": otp_code})
    assert token_resp.status_code == 200, token_resp.text
    return token_resp.json()["access_token"]


def register_and_login(client: TestClient, *, name: str, email: str, password: str, role: str) -> str:
    if role == "admin":
        return otp_login(client, phone="9000000001", role="admin", name=name)

    phone = phone_for_identity(role=role, email=email)
    r = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "phone": phone, "password": password, "role": role},
    )
    assert r.status_code == 200, r.text

    return otp_login(client, phone=phone, role=role, name=name)
