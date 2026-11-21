import os

import pytest
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402


@pytest.fixture(scope="session")
def app():
    url = os.getenv("TEST_DATABASE_URL")
    # Safety guard: never run tests on the real database
    assert url and url.rstrip("/").endswith("_test"), (
        "TEST_DATABASE_URL must exist and point to a database whose name ends with _test"
    )
    app = create_app({"SQLALCHEMY_DATABASE_URI": url, "TESTING": True})
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Empty all tables after every test so tests do not affect each other."""
    yield
    with app.app_context():
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(client):
    """Registers and logs in a user, returns the auth header."""

    def _make(email="a@example.com", password="StrongPass123"):
        client.post("/api/auth/register", json={"email": email, "password": password})
        res = client.post("/api/auth/login", json={"email": email, "password": password})
        return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

    return _make


@pytest.fixture
def user_a(make_user):
    return make_user("a@example.com")


@pytest.fixture
def user_b(make_user):
    return make_user("b@example.com")