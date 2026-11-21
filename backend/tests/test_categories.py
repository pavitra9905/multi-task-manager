def test_create_and_list_categories(client, user_a):
    res = client.post("/api/categories", json={"name": "Work"}, headers=user_a)
    assert res.status_code == 201
    listing = client.get("/api/categories", headers=user_a).get_json()
    assert [c["name"] for c in listing] == ["Work"]


def test_duplicate_category_same_user(client, user_a):
    client.post("/api/categories", json={"name": "Work"}, headers=user_a)
    res = client.post("/api/categories", json={"name": "Work"}, headers=user_a)
    assert res.status_code == 409


def test_same_category_name_allowed_for_different_users(client, user_a, user_b):
    assert client.post("/api/categories", json={"name": "Work"}, headers=user_a).status_code == 201
    assert client.post("/api/categories", json={"name": "Work"}, headers=user_b).status_code == 201


def test_empty_category_name_rejected(client, user_a):
    assert client.post("/api/categories", json={"name": "   "}, headers=user_a).status_code == 400


def test_rename_category(client, user_a):
    cat = client.post("/api/categories", json={"name": "Work"}, headers=user_a).get_json()
    res = client.put(f"/api/categories/{cat['id']}", json={"name": "Office"}, headers=user_a)
    assert res.status_code == 200
    assert res.get_json()["name"] == "Office"


def test_rename_to_existing_name_rejected(client, user_a):
    client.post("/api/categories", json={"name": "Work"}, headers=user_a)
    other = client.post("/api/categories", json={"name": "Study"}, headers=user_a).get_json()
    res = client.put(f"/api/categories/{other['id']}", json={"name": "Work"}, headers=user_a)
    assert res.status_code == 409


def test_deleting_category_keeps_tasks(client, user_a):
    cat = client.post("/api/categories", json={"name": "Work"}, headers=user_a).get_json()
    task = client.post("/api/tasks", json={"title": "keep me", "category_id": cat["id"]}, headers=user_a).get_json()

    assert client.delete(f"/api/categories/{cat['id']}", headers=user_a).status_code == 200

    res = client.get(f"/api/tasks/{task['id']}", headers=user_a)
    assert res.status_code == 200
    assert res.get_json()["category"] is None