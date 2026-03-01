from app.tests.conftest import register_and_login


def test_v2_booking_flow(client):
    supplier_token = register_and_login(
        client,
        name="Supplier V2",
        email="supplier-v2@example.com",
        password="secret123",
        role="supplier",
    )

    supplier_profile = client.post(
        "/api/v2/suppliers/profile",
        json={"business_name": "V2 Supplier", "phone": "9999999999", "address": "Village Road"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert supplier_profile.status_code == 200, supplier_profile.text
    v2_supplier_id = supplier_profile.json()["id"]

    doc = client.post(
        "/api/v2/suppliers/me/documents",
        json={"doc_type": "AADHAR", "file_url": "https://example.com/aadhar.png"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert doc.status_code == 200, doc.text

    admin_token = register_and_login(
        client,
        name="Admin V2",
        email="admin-v2@example.com",
        password="secret123",
        role="admin",
    )

    verified = client.post(
        f"/api/v2/suppliers/{v2_supplier_id}/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert verified.status_code == 200, verified.text
    assert verified.json()["status"] == "VERIFIED"

    buyer_token = register_and_login(
        client,
        name="Buyer V2",
        email="buyer-v2@example.com",
        password="secret123",
        role="user",
    )

    booking = client.post(
        "/api/v2/bookings",
        json={"supplier_id": v2_supplier_id, "description": "Need sand delivery"},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert booking.status_code == 200, booking.text
    booking_id = booking.json()["id"]
    assert booking.json()["status"] == "PENDING_SUPPLIER_APPROVAL"

    accepted = client.post(
        f"/api/v2/bookings/{booking_id}/accept",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "ACCEPTED"
