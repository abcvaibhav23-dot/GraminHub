from conftest import register_and_login


def test_supplier_approval_and_search_visibility(client):
    supplier_token = register_and_login(
        client,
        name="Supplier B",
        email="supplierB@example.com",
        password="secret123",
        role="supplier",
    )

    profile = client.post(
        "/api/suppliers/profile",
        json={"business_name": "B Transport", "phone": "8888888888", "address": "Depot Street"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200
    supplier_id = profile.json()["id"]
    service = client.post(
        "/api/suppliers/services",
        json={"category_id": 2, "item_name": "Mini Truck", "price": 3500, "availability": "available"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200

    before = client.get("/api/suppliers/search")
    assert before.status_code == 200
    assert all(s["id"] != supplier_id for s in before.json())

    admin_token = register_and_login(
        client,
        name="Admin B",
        email="adminB@example.com",
        password="secret123",
        role="admin",
    )
    approval = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approval.status_code == 200

    after = client.get("/api/suppliers/search")
    assert after.status_code == 200
    assert any(s["id"] == supplier_id for s in after.json())


def test_supplier_block_hides_from_search_and_blocks_calls(client):
    supplier_token = register_and_login(
        client,
        name="Supplier C",
        email="supplierC@example.com",
        password="secret123",
        role="supplier",
    )
    profile = client.post(
        "/api/suppliers/profile",
        json={"business_name": "C Rentals", "phone": "7777777777", "address": "Rental Chowk"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200
    supplier_id = profile.json()["id"]
    service = client.post(
        "/api/suppliers/services",
        json={"category_id": 1, "item_name": "Concrete Mixer", "price": 7000, "availability": "available"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200

    admin_token = register_and_login(
        client,
        name="Admin C",
        email="adminC@example.com",
        password="secret123",
        role="admin",
    )
    approve = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200

    visible = client.get("/api/suppliers/search")
    assert any(s["id"] == supplier_id for s in visible.json())

    block = client.post(
        f"/api/admin/suppliers/{supplier_id}/block",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert block.status_code == 200

    hidden = client.get("/api/suppliers/search")
    assert all(s["id"] != supplier_id for s in hidden.json())

    user_token = register_and_login(
        client,
        name="User C",
        email="userC@example.com",
        password="secret123",
        role="user",
    )
    call_resp = client.post(
        f"/api/suppliers/{supplier_id}/call",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert call_resp.status_code == 404


def test_supplier_search_supports_simple_keywords_with_category_filter(client):
    supplier_token = register_and_login(
        client,
        name="Supplier Keyword",
        email="supplier-keyword@example.com",
        password="secret123",
        role="supplier",
    )
    profile = client.post(
        "/api/suppliers/profile",
        json={
            "business_name": "Keyword Fleet",
            "phone": "9666666666",
            "address": "Industrial Transport Nagar",
        },
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200
    supplier_id = profile.json()["id"]

    service = client.post(
        "/api/suppliers/services",
        json={
            "category_id": 2,
            "item_name": "Heavy Transport Truck",
            "item_details": "Heavy request support",
            "price": 12000,
            "availability": "available on request",
        },
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200

    admin_token = register_and_login(
        client,
        name="Admin Keyword",
        email="admin-keyword@example.com",
        password="secret123",
        role="admin",
    )
    approve = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200

    keyword_only = client.get("/api/suppliers/search", params={"keyword": "heavy request"})
    assert keyword_only.status_code == 200
    assert any(row["id"] == supplier_id for row in keyword_only.json())

    keyword_with_category = client.get(
        "/api/suppliers/search",
        params={"category_id": 2, "keyword": "heavy request"},
    )
    assert keyword_with_category.status_code == 200
    assert any(row["id"] == supplier_id for row in keyword_with_category.json())

    wrong_category = client.get(
        "/api/suppliers/search",
        params={"category_id": 1, "keyword": "heavy"},
    )
    assert wrong_category.status_code == 200
    assert all(row["id"] != supplier_id for row in wrong_category.json())


def test_supplier_profile_creates_new_unique_id_without_overwriting_old_record(client):
    supplier_token = register_and_login(
        client,
        name="Supplier D",
        email="supplierD@example.com",
        password="secret123",
        role="supplier",
    )

    first = client.post(
        "/api/suppliers/profile",
        json={"business_name": "D Logistics One", "phone": "9000000001", "address": "Address 1"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert first.status_code == 200
    first_id = first.json()["id"]

    second = client.post(
        "/api/suppliers/profile",
        json={"business_name": "D Logistics Two", "phone": "9000000002", "address": "Address 2"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert second.status_code == 200
    second_id = second.json()["id"]

    third = client.post(
        "/api/suppliers/profile",
        json={"business_name": "D Logistics Three", "phone": "9000000003", "address": "Address 3"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert third.status_code == 200
    third_id = third.json()["id"]

    assert len({first_id, second_id, third_id}) == 3
    assert first_id < second_id < third_id

    admin_token = register_and_login(
        client,
        name="Admin D",
        email="adminD@example.com",
        password="secret123",
        role="admin",
    )
    pending = client.get(
        "/api/admin/pending-suppliers",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert pending.status_code == 200

    by_id = {row["id"]: row for row in pending.json()}
    assert by_id[first_id]["business_name"] == "D Logistics One"
    assert by_id[second_id]["business_name"] == "D Logistics Two"
    assert by_id[third_id]["business_name"] == "D Logistics Three"


def test_supplier_can_edit_existing_profile_and_service(client):
    supplier_token = register_and_login(
        client,
        name="Supplier Edit",
        email="supplier-edit@example.com",
        password="secret123",
        role="supplier",
    )

    profile = client.post(
        "/api/suppliers/profile",
        json={"business_name": "Edit Hub", "phone": "9111111111", "address": "Old Address"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200
    supplier_id = profile.json()["id"]

    service = client.post(
        "/api/suppliers/services",
        json={"category_id": 1, "item_name": "Cement Bag", "price": 2500, "availability": "available"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200
    service_id = service.json()["id"]

    update_profile = client.put(
        f"/api/suppliers/profiles/{supplier_id}",
        json={"business_name": "Edit Hub Updated", "phone": "9222222222", "address": "New Address"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert update_profile.status_code == 200
    assert update_profile.json()["business_name"] == "Edit Hub Updated"
    assert update_profile.json()["phone"] == "9222222222"

    update_service = client.put(
        f"/api/suppliers/services/{service_id}",
        json={"price": 3100, "availability": "on request"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert update_service.status_code == 200
    assert float(update_service.json()["price"]) == 3100.0
    assert update_service.json()["availability"] == "on request"

    service_list = client.get(
        "/api/suppliers/me/services",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service_list.status_code == 200
    assert any(row["id"] == service_id for row in service_list.json())


def test_admin_can_edit_supplier_profile_and_service_by_id(client):
    supplier_token = register_and_login(
        client,
        name="Supplier For Admin Edit",
        email="supplier-admin-edit@example.com",
        password="secret123",
        role="supplier",
    )
    profile = client.post(
        "/api/suppliers/profile",
        json={"business_name": "Admin Edit Supplier", "phone": "9333333333", "address": "Supplier Address"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200
    supplier_id = profile.json()["id"]

    service = client.post(
        "/api/suppliers/services",
        json={"category_id": 1, "item_name": "Crusher Sand", "price": 4000, "availability": "available"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200
    service_id = service.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin Edit Supplier",
        email="admin-edit-supplier@example.com",
        password="secret123",
        role="admin",
    )

    update_profile = client.put(
        f"/api/suppliers/profiles/{supplier_id}",
        json={"business_name": "Admin Updated Name", "phone": "9444444444", "address": "Admin Updated Address"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert update_profile.status_code == 200
    assert update_profile.json()["business_name"] == "Admin Updated Name"

    update_service = client.put(
        f"/api/suppliers/services/{service_id}",
        json={"price": 5200},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert update_service.status_code == 200
    assert float(update_service.json()["price"]) == 5200.0


def test_search_returns_item_details_and_photos(client):
    supplier_token = register_and_login(
        client,
        name="Supplier Item Card",
        email="supplier-item-card@example.com",
        password="secret123",
        role="supplier",
    )
    profile = client.post(
        "/api/suppliers/profile",
        json={"business_name": "Item Card Supplier", "phone": "9555511111", "address": "Item Market"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200
    supplier_id = profile.json()["id"]

    service = client.post(
        "/api/suppliers/services",
        json={
            "category_id": 1,
            "item_name": "PPC Cement",
            "item_details": "53 grade",
            "item_variant": "50kg bag",
            "photo_url_1": "https://example.com/cement1.jpg",
            "photo_url_2": "https://example.com/cement2.jpg",
            "availability": "in stock",
        },
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200

    admin_token = register_and_login(
        client,
        name="Admin Item Card",
        email="admin-item-card@example.com",
        password="secret123",
        role="admin",
    )
    approve = client.post(
        f"/api/admin/suppliers/{supplier_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve.status_code == 200

    search = client.get("/api/suppliers/search", params={"keyword": "cement 53"})
    assert search.status_code == 200
    row = next((item for item in search.json() if item["id"] == supplier_id), None)
    assert row is not None
    assert row["services"]
    first_item = row["services"][0]
    assert first_item["item_name"] == "PPC Cement"
    assert first_item["item_variant"] == "50kg bag"
    assert first_item["photo_url_1"] == "https://example.com/cement1.jpg"


def test_admin_can_delete_supplier_service(client):
    supplier_token = register_and_login(
        client,
        name="Supplier Delete Service",
        email="supplier-delete-service@example.com",
        password="secret123",
        role="supplier",
    )
    profile = client.post(
        "/api/suppliers/profile",
        json={"business_name": "Delete Service Hub", "phone": "9555522222", "address": "Delete Road"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert profile.status_code == 200

    service = client.post(
        "/api/suppliers/services",
        json={"item_name": "Bricks", "price": 900, "availability": "available"},
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert service.status_code == 200
    service_id = service.json()["id"]

    admin_token = register_and_login(
        client,
        name="Admin Delete Service",
        email="admin-delete-service@example.com",
        password="secret123",
        role="admin",
    )
    delete_resp = client.delete(
        f"/api/suppliers/services/{service_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_resp.status_code == 200

    services_after = client.get(
        "/api/suppliers/me/services",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert services_after.status_code == 200
    assert all(row["id"] != service_id for row in services_after.json())
