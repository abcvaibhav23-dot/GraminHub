from conftest import register_and_login


def test_admin_can_delete_supplier_by_id(client):
    supplier_token = register_and_login(
        client,
        name="Supplier Delete",
        email="supplier-delete@example.com",
        password="secret123",
        role="supplier",
    )
    profile = client.post(
        "/api/suppliers/profile",
        json={"business_name": "Delete Me Supplier", "phone": "9555555555", "address": "Delete Street"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200
    supplier_id = profile.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin Delete Supplier",
        email="admin-delete-supplier@example.com",
        password="secret123",
        role="admin",
    )
    approve = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200

    before_delete = client.get("/api/suppliers/search")
    assert any(row["id"] == supplier_id for row in before_delete.json())

    deleted = client.delete(
        f"/api/admin/suppliers/{supplier_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert deleted.status_code == 200
    assert deleted.json()["message"] == "Supplier deleted"

    after_delete = client.get("/api/suppliers/search")
    assert all(row["id"] != supplier_id for row in after_delete.json())


def test_admin_can_delete_user_but_cannot_delete_self(client):
    user_token = register_and_login(
        client,
        name="Delete Target User",
        email="delete-target@example.com",
        password="secret123",
        role="user",
    )
    user_me = client.get("/api/users/me", headers={"Authorization": f"Bearer {user_token}"})
    assert user_me.status_code == 200
    target_user_id = user_me.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin Delete User",
        email="admin-delete-user@example.com",
        password="secret123",
        role="admin",
    )
    admin_me = client.get("/api/users/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_me.status_code == 200
    admin_id = admin_me.json()["id"]

    deleted = client.delete(
        f"/api/admin/users/{target_user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert deleted.status_code == 200
    assert deleted.json()["message"] == "User deleted"

    deleted_login = client.post(
        "/api/auth/login",
        json={"email": "delete-target@example.com", "password": "secret123"},
    )
    assert deleted_login.status_code == 401

    self_delete = client.delete(
        f"/api/admin/users/{admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert self_delete.status_code == 409
    assert self_delete.json()["detail"] == "Admin cannot delete own account"

