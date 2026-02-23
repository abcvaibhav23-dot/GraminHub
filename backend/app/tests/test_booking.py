from conftest import register_and_login


def test_booking_creation(client):
    supplier_token = register_and_login(
        client,
        name="Supplier A",
        email="supplierA@example.com",
        password="secret123",
        role="supplier",
    )

    profile_resp = client.post(
        "/api/suppliers/profile",
        json={"business_name": "A Materials", "phone": "9999999999", "address": "Yard Road"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile_resp.status_code == 200
    supplier_id = profile_resp.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin A",
        email="adminA@example.com",
        password="secret123",
        role="admin",
    )

    approve = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200

    user_token = register_and_login(
        client,
        name="User A",
        email="userA@example.com",
        password="secret123",
        role="user",
    )

    booking = client.post(
        "/api/bookings",
        json={"supplier_id": supplier_id, "description": "Need 50 bags of cement"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert booking.status_code == 200
    assert booking.json()["status"] == "pending"


def test_whatsapp_booking_creation(client):
    supplier_token = register_and_login(
        client,
        name="Supplier WA",
        email="supplierwa@example.com",
        password="secret123",
        role="supplier",
    )

    profile_resp = client.post(
        "/api/suppliers/profile",
        json={"business_name": "WA Transport", "phone": "9876543210", "address": "Main Road"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile_resp.status_code == 200
    supplier_id = profile_resp.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin WA",
        email="adminwa@example.com",
        password="secret123",
        role="admin",
    )
    approve = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200

    user_token = register_and_login(
        client,
        name="User WA",
        email="userwa@example.com",
        password="secret123",
        role="user",
    )

    booking = client.post(
        "/api/bookings/whatsapp",
        json={"supplier_id": supplier_id, "description": "Need vehicle for 1 day"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert booking.status_code == 200
    data = booking.json()
    assert data["status"] == "pending"
    assert isinstance(data["booking_id"], int)
    assert "wa.me" in data["whatsapp_url"]


def test_guest_whatsapp_booking_without_login(client):
    supplier_token = register_and_login(
        client,
        name="Supplier G",
        email="supplierG@example.com",
        password="secret123",
        role="supplier",
    )
    profile_resp = client.post(
        "/api/suppliers/profile",
        json={"business_name": "Guest Rentals", "phone": "9123456789", "address": "Bypass Road"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile_resp.status_code == 200
    supplier_id = profile_resp.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin G",
        email="adminG@example.com",
        password="secret123",
        role="admin",
    )
    approve = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200

    booking = client.post(
        "/api/bookings/guest/whatsapp",
        json={
            "supplier_id": supplier_id,
            "description": "Need tractor for 1 day",
            "guest_name": "Ravi",
            "guest_phone": "9876500000",
        },
    )
    assert booking.status_code == 200
    data = booking.json()
    assert data["status"] == "pending"
    assert "wa.me" in data["whatsapp_url"]


def test_supplier_cannot_create_buyer_booking(client):
    supplier_token = register_and_login(
        client,
        name="Supplier No Buyer Actions",
        email="supplier-no-book@example.com",
        password="secret123",
        role="supplier",
    )
    profile_resp = client.post(
        "/api/suppliers/profile",
        json={"business_name": "Supplier Lockdown", "phone": "9333311111", "address": "Lockdown Road"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile_resp.status_code == 200
    supplier_id = profile_resp.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin Booking Guard",
        email="admin-booking-guard@example.com",
        password="secret123",
        role="admin",
    )
    approve = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200

    denied = client.post(
        "/api/bookings",
        json={"supplier_id": supplier_id, "description": "Supplier trying buyer booking"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert denied.status_code == 403
