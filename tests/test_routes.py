def test_login_page(client):
    assert client.get("/login").status_code == 200


def test_first_user_becomes_admin(client, app):
    from app.models import User, Role
    client.post("/registro", data={
        "name": "Primero", "email": "primero@x.com",
        "password": "Clave1234", "confirm": "Clave1234",
    }, follow_redirects=True)
    u = User.query.filter_by(email="primero@x.com").first()
    assert u is not None and u.role_name == Role.ADMIN


def test_dashboard_requires_login(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (301, 302)
    assert "/login" in r.headers["Location"]


def test_authenticated_dashboard(auth_client):
    r = auth_client.get("/")
    assert r.status_code == 200
    assert b"Dashboard" in r.data


def test_create_project_flow(auth_client, app):
    from app.models import Project
    auth_client.post("/proyectos/nuevo", data={
        "name": "Proyecto QA", "description": "d",
        "status": "activo", "priority": "media",
        "manager_id": "0", "team_id": "0",
    }, follow_redirects=True)
    assert Project.query.filter_by(name="Proyecto QA").count() == 1


def test_api_gantt_forbidden_without_login(client):
    assert client.get("/api/projects/1/gantt").status_code in (302, 401)
