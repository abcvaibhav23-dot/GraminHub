from conftest import register_and_login


def test_supplier_rating_flow(client):
    supplier_token = register_and_login(
        client,
        name="Supplier R",
        email="supplierR@example.com",
        password="secret123",
        role="supplier",
    )
    profile = client.post(
        "/api/suppliers/profile",
        json={"business_name": "R Stone Works", "phone": "6666666666", "address": "Stone Market"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200
    supplier_id = profile.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin R",
        email="adminR@example.com",
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
        name="User R",
        email="userR@example.com",
        password="secret123",
        role="user",
    )
    review = client.post(
        f"/api/suppliers/{supplier_id}/reviews",
        json={"supplier_id": supplier_id, "rating": 4, "comment": "Service thik thi"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert review.status_code == 200
    assert review.json()["rating"] == 4

    summary = client.get("/api/suppliers/search")
    supplier_rows = [row for row in summary.json() if row["id"] == supplier_id]
    assert supplier_rows
    assert supplier_rows[0]["total_reviews"] >= 1
    assert float(supplier_rows[0]["average_rating"]) >= 4.0
