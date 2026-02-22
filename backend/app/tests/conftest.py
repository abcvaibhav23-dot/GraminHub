from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_FILE = Path("/tmp/marketplace_test.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.core.config import Base, get_db
from app.main import app
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
    with TestClient(app) as c:
        yield c


def register_and_login(client: TestClient, *, name: str, email: str, password: str, role: str) -> str:
    r = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password, "role": role},
    )
    assert r.status_code == 200, r.text

    token_resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert token_resp.status_code == 200, token_resp.text
    return token_resp.json()["access_token"]
