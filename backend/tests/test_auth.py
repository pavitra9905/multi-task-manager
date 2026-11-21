from extensions import db
from models import User


def test_register_success(client):
    res = client.post("/api/auth/register", json={"email": "x@example.com", "password": "StrongPass123"})
    assert res.status_code == 201
    assert res.get_json()["user"]["email"] == "x@example.com"


def test_register_duplicate_email(client):
    body = {"email": "x@example.com", "password": "StrongPass123"}
    client.post("/api/auth/register", json=body)
    res = client.post("/api/auth/register", json=body)
    assert res.status_code == 409


def test_register_email_is_case_insensitive(client):
    client.post("/api/auth/register", json={"email": "x@example.com", "password": "StrongPass123"})
    res = client.post("/api/auth/register", json={"email": "X@Example.com", "password": "StrongPass123"})
    assert res.status_code == 409


def test_register_short_password(client):
    res = client.post("/api/auth/register", json={"email": "x@example.com", "password": "123"})
    assert res.status_code == 400
    assert "password" in res.get_json()["errors"]


def test_register_invalid_email(client):
    res = client.post("/api/auth/register", json={"email": "not-an-email", "password": "StrongPass123"})
    assert res.status_code == 400


def test_register_missing_body(client):
    res = client.post("/api/auth/register")
    assert res.status_code == 400


def test_password_is_hashed_in_database(app, client):
    client.post("/api/auth/register", json={"email": "x@example.com", "password": "StrongPass123"})
    with app.app_context():
        user = db.session.execute(db.select(User)).scalar_one()
        assert user.password_hash != "StrongPass123"
        assert user.password_hash.startswith("$2b$")


def test_login_success_returns_token(client):
    client.post("/api/auth/register", json={"email": "x@example.com", "password": "StrongPass123"})
    res = client.post("/api/auth/login", json={"email": "x@example.com", "password": "StrongPass123"})
    assert res.status_code == 200
    assert res.get_json()["access_token"]


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"email": "x@example.com", "password": "StrongPass123"})
    res = client.post("/api/auth/login", json={"email": "x@example.com", "password": "WrongPass999"})
    assert res.status_code == 401


def test_login_unknown_email_gives_same_message(client):
    client.post("/api/auth/register", json={"email": "x@example.com", "password": "StrongPass123"})
    wrong_pw = client.post("/api/auth/login", json={"email": "x@example.com", "password": "WrongPass999"})
    no_user = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "WrongPass999"})
    assert no_user.status_code == 401
    assert no_user.get_json() == wrong_pw.get_json()


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_garbage_token(client):
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.token"})
    assert res.status_code == 401


def test_me_with_token(client, user_a):
    res = client.get("/api/auth/me", headers=user_a)
    assert res.status_code == 200
    assert res.get_json()["email"] == "a@example.com"