def create_task(client, headers, **overrides):
    body = {"title": "Write report"}
    body.update(overrides)
    return client.post("/api/tasks", json=body, headers=headers)


def test_tasks_require_login(client):
    assert client.get("/api/tasks").status_code == 401
    assert client.post("/api/tasks", json={"title": "x"}).status_code == 401


def test_create_task_defaults(client, user_a):
    res = create_task(client, user_a)
    assert res.status_code == 201
    data = res.get_json()
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["category"] is None


def test_create_task_empty_title(client, user_a):
    assert create_task(client, user_a, title="   ").status_code == 400


def test_create_task_missing_title(client, user_a):
    res = client.post("/api/tasks", json={}, headers=user_a)
    assert res.status_code == 400


def test_create_task_bad_priority(client, user_a):
    assert create_task(client, user_a, priority="urgent").status_code == 400


def test_create_task_bad_status(client, user_a):
    assert create_task(client, user_a, status="banana").status_code == 400


def test_create_task_bad_date(client, user_a):
    assert create_task(client, user_a, due_date="not-a-date").status_code == 400


def test_create_task_rejects_unknown_user_id_field(client, user_a):
    res = create_task(client, user_a, user_id=999)
    assert res.status_code == 400
    assert "user_id" in res.get_json()["errors"]


def test_title_too_long(client, user_a):
    assert create_task(client, user_a, title="x" * 151).status_code == 400


def test_list_returns_only_own_tasks(client, user_a):
    create_task(client, user_a, title="one")
    create_task(client, user_a, title="two")
    res = client.get("/api/tasks", headers=user_a)
    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_get_single_task(client, user_a):
    task_id = create_task(client, user_a).get_json()["id"]
    res = client.get(f"/api/tasks/{task_id}", headers=user_a)
    assert res.status_code == 200
    assert res.get_json()["id"] == task_id


def test_update_task(client, user_a):
    task_id = create_task(client, user_a).get_json()["id"]
    res = client.put(f"/api/tasks/{task_id}", json={"status": "done", "title": "  New title  "}, headers=user_a)
    assert res.status_code == 200
    assert res.get_json()["status"] == "done"
    assert res.get_json()["title"] == "New title"


def test_update_task_rejects_empty_title(client, user_a):
    task_id = create_task(client, user_a).get_json()["id"]
    res = client.put(f"/api/tasks/{task_id}", json={"title": ""}, headers=user_a)
    assert res.status_code == 400


def test_delete_task(client, user_a):
    task_id = create_task(client, user_a).get_json()["id"]
    assert client.delete(f"/api/tasks/{task_id}", headers=user_a).status_code == 200
    assert client.get(f"/api/tasks/{task_id}", headers=user_a).status_code == 404


def test_missing_task_returns_404(client, user_a):
    assert client.get("/api/tasks/99999", headers=user_a).status_code == 404


def test_filter_by_status(client, user_a):
    create_task(client, user_a, title="a", status="todo")
    create_task(client, user_a, title="b", status="done")
    res = client.get("/api/tasks?status=done", headers=user_a)
    titles = [t["title"] for t in res.get_json()]
    assert titles == ["b"]


def test_filter_by_priority(client, user_a):
    create_task(client, user_a, title="a", priority="high")
    create_task(client, user_a, title="b", priority="low")
    res = client.get("/api/tasks?priority=high", headers=user_a)
    assert [t["title"] for t in res.get_json()] == ["a"]


def test_filter_by_category(client, user_a):
    cat = client.post("/api/categories", json={"name": "Work"}, headers=user_a).get_json()
    create_task(client, user_a, title="in work", category_id=cat["id"])
    create_task(client, user_a, title="no category")
    res = client.get(f"/api/tasks?category_id={cat['id']}", headers=user_a)
    assert [t["title"] for t in res.get_json()] == ["in work"]


def test_search_is_case_insensitive(client, user_a):
    create_task(client, user_a, title="Finish REPORT")
    create_task(client, user_a, title="Buy milk")
    res = client.get("/api/tasks?q=report", headers=user_a)
    assert [t["title"] for t in res.get_json()] == ["Finish REPORT"]


def test_combined_filters(client, user_a):
    create_task(client, user_a, title="a", status="done", priority="high")
    create_task(client, user_a, title="b", status="done", priority="low")
    res = client.get("/api/tasks?status=done&priority=high", headers=user_a)
    assert [t["title"] for t in res.get_json()] == ["a"]


def test_bad_filter_values_rejected(client, user_a):
    assert client.get("/api/tasks?status=banana", headers=user_a).status_code == 400
    assert client.get("/api/tasks?priority=urgent", headers=user_a).status_code == 400