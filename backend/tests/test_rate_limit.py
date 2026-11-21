CREDS = {"email": "victim@example.com", "password": "StrongPass123"}


def bad_login(client, email="victim@example.com", ip=None):
    kwargs = {"environ_overrides": {"REMOTE_ADDR": ip}} if ip else {}
    return client.post("/api/auth/login", json={"email": email, "password": "WrongPass999"}, **kwargs)


def test_login_is_blocked_after_too_many_attempts_from_one_ip(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "LOGIN_RATE_LIMIT", "3 per minute")
    client.post("/api/auth/register", json=CREDS)

    codes = [bad_login(client, email=f"user{i}@example.com").status_code for i in range(5)]
    assert codes == [401, 401, 401, 429, 429]


def test_blocked_response_is_clean_json(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "LOGIN_RATE_LIMIT", "1 per minute")
    bad_login(client)
    res = bad_login(client)
    assert res.status_code == 429
    assert "Too many attempts" in res.get_json()["error"]


def test_one_email_is_limited_even_when_attacker_changes_ip(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "LOGIN_EMAIL_RATE_LIMIT", "2 per minute")
    codes = [bad_login(client, ip=f"10.0.0.{i}").status_code for i in range(1, 5)]
    assert codes == [401, 401, 429, 429]


def test_other_emails_are_not_blocked_by_one_victims_limit(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "LOGIN_EMAIL_RATE_LIMIT", "1 per minute")
    bad_login(client, email="one@example.com", ip="10.0.0.1")
    assert bad_login(client, email="one@example.com", ip="10.0.0.2").status_code == 429
    assert bad_login(client, email="two@example.com", ip="10.0.0.3").status_code == 401


def test_successful_login_still_works_under_the_limit(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "LOGIN_RATE_LIMIT", "3 per minute")
    client.post("/api/auth/register", json=CREDS)
    res = client.post("/api/auth/login", json=CREDS)
    assert res.status_code == 200


def test_register_is_limited(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "REGISTER_RATE_LIMIT", "2 per hour")
    codes = [
        client.post("/api/auth/register", json={"email": f"n{i}@example.com", "password": "StrongPass123"}).status_code
        for i in range(4)
    ]
    assert codes == [201, 201, 429, 429]


def test_other_routes_are_not_rate_limited(client, user_a):
    for _ in range(30):
        assert client.get("/api/tasks", headers=user_a).status_code == 200