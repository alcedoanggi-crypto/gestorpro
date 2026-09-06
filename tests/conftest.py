import pytest

from app import create_app
from app.extensions import db as _db
from app.models import Role, User


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        Role.seed_defaults()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin(app):
    u = User(name="Admin Test", email="admin@test.com", role=Role.get(Role.ADMIN))
    u.set_password("Secret123")
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture()
def auth_client(client, admin):
    client.post("/login", data={"email": "admin@test.com", "password": "Secret123"},
                follow_redirects=True)
    return client
