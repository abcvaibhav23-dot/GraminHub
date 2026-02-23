from conftest import otp_login, register_and_login


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
    service = client.post(
        "/api/suppliers/services",
        json={"category_id": 1, "item_name": "Stone Chips", "price": 1300, "availability": "in stock"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200

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

    deleted_profile_access = client.get("/api/users/me", headers={"Authorization": f"Bearer {user_token}"})
    assert deleted_profile_access.status_code == 401

    self_delete = client.delete(
        f"/api/admin/users/{admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert self_delete.status_code == 409
    assert self_delete.json()["detail"] == "Admin cannot delete own account"


def test_admin_can_manage_users_suppliers_and_items(client):
    admin_token = register_and_login(
        client,
        name="Admin Manage",
        email="admin-manage@example.com",
        password="secret123",
        role="admin",
    )

    create_user = client.post(
        "/api/admin/users",
        json={"name": "Managed Buyer", "phone": "9011111111", "role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_user.status_code == 200
    managed_user_id = create_user.json()["id"]

    block_user = client.post(
        f"/api/admin/users/{managed_user_id}/block",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert block_user.status_code == 200

    blocked_otp = client.post(
        "/api/auth/otp/request",
        json={"phone": "9011111111", "role": "user", "name": "Managed Buyer"},
    )
    assert blocked_otp.status_code == 403

    unblock_user = client.post(
        f"/api/admin/users/{managed_user_id}/unblock",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert unblock_user.status_code == 200

    unblocked_user_token = otp_login(client, phone="9011111111", role="user", name="Managed Buyer")
    unblocked_user_me = client.get("/api/users/me", headers={"Authorization": f"Bearer {unblocked_user_token}"})
    assert unblocked_user_me.status_code == 200

    create_supplier = client.post(
        "/api/admin/suppliers",
        json={
            "owner_name": "Managed Supplier Owner",
            "owner_phone": "9022222222",
            "business_name": "Managed Supplier Biz",
            "supplier_phone": "9033333333",
            "address": "Managed Address",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_supplier.status_code == 200
    supplier_id = create_supplier.json()["id"]
    assert create_supplier.json()["approved"] is True

    supplier_token = otp_login(client, phone="9022222222", role="supplier", name="Managed Supplier Owner")
    service = client.post(
        "/api/suppliers/services",
        json={"item_name": "Managed Item", "price": 2400, "availability": "available"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200
    service_id = service.json()["id"]

    delete_item = client.delete(
        f"/api/admin/services/{service_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_item.status_code == 200

    supplier_services = client.get(
        "/api/suppliers/me/services",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert supplier_services.status_code == 200
    assert all(row["id"] != service_id for row in supplier_services.json())

    # Supplier exists and was admin-created with valid ID.
    search = client.get("/api/suppliers/search")
    assert search.status_code == 200
    assert all(row["id"] != supplier_id for row in search.json())  # hidden until at least one active item exists
