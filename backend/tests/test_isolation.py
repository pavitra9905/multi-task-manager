def make_task_for(client, headers, title="private task"):
    return client.post("/api/tasks", json={"title": title}, headers=headers).get_json()


def test_user_b_does_not_see_user_a_tasks(client, user_a, user_b):
    make_task_for(client, user_a)
    res = client.get("/api/tasks", headers=user_b)
    assert res.get_json()["items"] == []


def test_user_b_cannot_read_user_a_task(client, user_a, user_b):
    task = make_task_for(client, user_a)
    assert client.get(f"/api/tasks/{task['id']}", headers=user_b).status_code == 404


def test_user_b_cannot_edit_user_a_task(client, user_a, user_b):
    task = make_task_for(client, user_a)
    res = client.put(f"/api/tasks/{task['id']}", json={"title": "hacked"}, headers=user_b)
    assert res.status_code == 404
    # The task must be unchanged
    original = client.get(f"/api/tasks/{task['id']}", headers=user_a).get_json()
    assert original["title"] == "private task"


def test_user_b_cannot_delete_user_a_task(client, user_a, user_b):
    task = make_task_for(client, user_a)
    assert client.delete(f"/api/tasks/{task['id']}", headers=user_b).status_code == 404
    # The task must still exist
    assert client.get(f"/api/tasks/{task['id']}", headers=user_a).status_code == 200


def test_user_b_cannot_see_user_a_categories(client, user_a, user_b):
    client.post("/api/categories", json={"name": "Secret"}, headers=user_a)
    assert client.get("/api/categories", headers=user_b).get_json() == []


def test_user_b_cannot_edit_or_delete_user_a_category(client, user_a, user_b):
    cat = client.post("/api/categories", json={"name": "Secret"}, headers=user_a).get_json()
    assert client.put(f"/api/categories/{cat['id']}", json={"name": "x"}, headers=user_b).status_code == 404
    assert client.delete(f"/api/categories/{cat['id']}", headers=user_b).status_code == 404


def test_user_b_cannot_attach_task_to_user_a_category(client, user_a, user_b):
    cat = client.post("/api/categories", json={"name": "Secret"}, headers=user_a).get_json()
    res = client.post("/api/tasks", json={"title": "sneaky", "category_id": cat["id"]}, headers=user_b)
    assert res.status_code == 400


def test_user_b_cannot_move_own_task_into_user_a_category(client, user_a, user_b):
    cat = client.post("/api/categories", json={"name": "Secret"}, headers=user_a).get_json()
    task = make_task_for(client, user_b, "mine")
    res = client.put(f"/api/tasks/{task['id']}", json={"category_id": cat["id"]}, headers=user_b)
    assert res.status_code == 400


def test_filters_do_not_leak_other_users_data(client, user_a, user_b):
    make_task_for(client, user_a, "A's secret report")
    res = client.get("/api/tasks?q=report", headers=user_b)
    assert res.get_json()["items"] == []