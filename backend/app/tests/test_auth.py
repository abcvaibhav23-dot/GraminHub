from conftest import otp_login, register_and_login
from app.core.config import settings


def test_user_registration_and_login(client):
    phone = "9000000010"
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "User One",
            "email": "user1@example.com",
            "phone": phone,
            "password": "secret123",
            "role": "user",
        },
    )
    assert reg.status_code == 200
    assert reg.json()["email"] == "user1@example.com"
    registered_user_id = reg.json()["id"]

    token = otp_login(client, phone=phone, role="user", name="User One")
    assert token
    me = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["id"] == registered_user_id


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


def test_public_admin_registration_is_blocked(client):
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "Public Admin",
            "email": "public-admin@example.com",
            "phone": "9000000999",
            "password": "secret123",
            "role": "admin",
        },
    )
    assert reg.status_code == 403
    assert reg.json()["detail"] == "Admin registration is restricted"


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

    me_after_update = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_after_update.status_code == 200
    phone = me_after_update.json()["phone"]

    relogin_token = otp_login(client, phone=phone, role="user", name="Updated User")
    assert relogin_token


def test_phone_otp_login_for_user_and_supplier(client):
    otp_user = client.post(
        "/api/auth/otp/request",
        json={"phone": "9000000101", "role": "user", "name": "OTP User"},
    )
    assert otp_user.status_code == 200
    user_otp_code = otp_user.json()["otp"]
    assert len(user_otp_code) == settings.OTP_CODE_LENGTH

    verify_user = client.post(
        "/api/auth/otp/verify",
        json={"phone": "9000000101", "role": "user", "otp": user_otp_code},
    )
    assert verify_user.status_code == 200
    user_token = verify_user.json()["access_token"]

    user_me = client.get("/api/users/me", headers={"Authorization": f"Bearer {user_token}"})
    assert user_me.status_code == 200
    assert user_me.json()["role"] == "user"

    otp_supplier = client.post(
        "/api/auth/otp/request",
        json={"phone": "9000000102", "role": "supplier", "name": "OTP Supplier"},
    )
    assert otp_supplier.status_code == 200
    supplier_otp_code = otp_supplier.json()["otp"]
    assert len(supplier_otp_code) == settings.OTP_CODE_LENGTH

    verify_supplier = client.post(
        "/api/auth/otp/verify",
        json={"phone": "9000000102", "role": "supplier", "otp": supplier_otp_code},
    )
    assert verify_supplier.status_code == 200
    supplier_token = verify_supplier.json()["access_token"]

    supplier_me = client.get("/api/users/me", headers={"Authorization": f"Bearer {supplier_token}"})
    assert supplier_me.status_code == 200
    assert supplier_me.json()["role"] == "supplier"


def test_admin_otp_login_allowlist_and_role(client):
    otp_admin = client.post(
        "/api/auth/otp/request",
        json={"phone": "9000000001", "role": "admin", "name": "Owner Admin"},
    )
    assert otp_admin.status_code == 200
    admin_otp = otp_admin.json()["otp"]

    verify_admin = client.post(
        "/api/auth/otp/verify",
        json={"phone": "9000000001", "role": "admin", "otp": admin_otp},
    )
    assert verify_admin.status_code == 200
    admin_token = verify_admin.json()["access_token"]
    admin_me = client.get("/api/users/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_me.status_code == 200
    assert admin_me.json()["role"] == "admin"

    blocked_admin = client.post(
        "/api/auth/otp/request",
        json={"phone": "9000000999", "role": "admin", "name": "Blocked Admin"},
    )
    assert blocked_admin.status_code == 403
