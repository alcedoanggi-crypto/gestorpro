from datetime import date, timedelta

from app.extensions import db
from app.models import Project, Role, Task, User
from app.models.enums import TaskStatus


def test_password_hashing(app):
    u = User(name="X", email="x@x.com", role=Role.get(Role.COLLABORATOR))
    u.set_password("MiClave123")
    assert u.password_hash != "MiClave123"
    assert u.check_password("MiClave123")
    assert not u.check_password("otra")


def test_reset_token_roundtrip(app):
    u = User(name="X", email="r@x.com", role=Role.get(Role.COLLABORATOR))
    token = u.generate_reset_token(ttl_hours=1)
    assert u.verify_reset_token(token)
    assert not u.verify_reset_token("malo")
    u.clear_reset_token()
    assert not u.verify_reset_token(token)


def test_project_progress_and_overdue(app):
    m = User(name="M", email="m@x.com", role=Role.get(Role.MANAGER))
    m.set_password("Secret123")
    db.session.add(m)
    db.session.flush()
    p = Project(name="P", manager=m)
    db.session.add(p)
    db.session.flush()
    db.session.add_all([
        Task(title="a", project=p, status=TaskStatus.DONE),
        Task(title="b", project=p, status=TaskStatus.TODO,
             due_date=date.today() - timedelta(days=1)),
    ])
    db.session.commit()
    assert p.progress == 50
    assert p.overdue_task_count == 1


def test_task_to_gantt_shape(app):
    p = Project(name="P2")
    db.session.add(p)
    db.session.flush()
    t = Task(title="t", project=p, start_date=date.today(),
             due_date=date.today() + timedelta(days=3), progress=25)
    db.session.add(t)
    db.session.commit()
    g = t.to_gantt()
    assert g["id"] == str(t.id)
    assert g["progress"] == 25
    assert "start" in g and "end" in g
