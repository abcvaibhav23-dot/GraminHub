from conftest import register_and_login


def test_user_registration_and_login(client):
    reg = client.post(
        "/api/auth/register",
        json={"name": "User One", "email": "user1@example.com", "password": "secret123", "role": "user"},
    )
    assert reg.status_code == 200
    assert reg.json()["email"] == "user1@example.com"

    login = client.post("/api/auth/login", json={"email": "user1@example.com", "password": "secret123"})
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_auth_protection_requires_token(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_auth_protection_with_token(client):
    token = register_and_login(
        client,
        name="Protected User",
        email="protected@example.com",
        password="secret123",
        role="user",
    )
    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "protected@example.com"


def test_duplicate_registration_returns_conflict(client):
    payload = {
        "name": "Dup User",
        "email": "dup@example.com",
        "password": "secret123",
        "role": "user",
    }
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 200

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"] == "Email already exists"


def test_request_id_header_exists(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert "X-Request-ID" in health.headers


def test_user_can_edit_own_profile(client):
    token = register_and_login(
        client,
        name="Edit Profile User",
        email="edit-profile@example.com",
        password="secret123",
        role="user",
    )

    update = client.put(
        "/api/users/me",
        json={"name": "Updated User", "email": "updated-profile@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update.status_code == 200
    assert update.json()["name"] == "Updated User"
    assert update.json()["email"] == "updated-profile@example.com"

    relogin = client.post(
        "/api/auth/login",
        json={"email": "updated-profile@example.com", "password": "secret123"},
    )
    assert relogin.status_code == 200
