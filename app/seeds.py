"""Datos de demostracion. Uso: flask seed"""
from datetime import date, datetime, timedelta

from .extensions import db
from .models import (Comment, Project, Role, Task, Team, User)
from .models.enums import Priority, ProjectStatus, TaskStatus


def run_seed():
    db.create_all()
    Role.seed_defaults()

    if User.query.count() > 0:
        print("Ya hay datos. Aborta el seed para no duplicar.")
        return

    admin_r = Role.get(Role.ADMIN)
    manager_r = Role.get(Role.MANAGER)
    collab_r = Role.get(Role.COLLABORATOR)

    def mkuser(name, email, role, title):
        u = User(name=name, email=email, role=role, job_title=title)
        u.set_password("Demo1234")
        db.session.add(u)
        return u

    admin = mkuser("Ana Torres", "admin@demo.com", admin_r, "Directora de PMO")
    gerente1 = mkuser("Bruno Diaz", "gerente@demo.com", manager_r, "Gerente de Proyectos")
    gerente2 = mkuser("Carla Ruiz", "carla@demo.com", manager_r, "Gerente de Producto")
    dev1 = mkuser("Diego Lopez", "diego@demo.com", collab_r, "Desarrollador Backend")
    dev2 = mkuser("Elena Marin", "elena@demo.com", collab_r, "Desarrolladora Frontend")
    des1 = mkuser("Franco Vega", "franco@demo.com", collab_r, "Disenador UX")
    qa1 = mkuser("Gabriela Sol", "gabriela@demo.com", collab_r, "QA Engineer")
    db.session.flush()

    t_web = Team(name="Plataforma Web", description="Equipo full-stack del producto principal")
    t_web.members = [gerente1, dev1, dev2, des1, qa1]
    t_mobile = Team(name="Movil", description="Aplicaciones iOS y Android")
    t_mobile.members = [gerente2, dev2, qa1]
    db.session.add_all([t_web, t_mobile])
    db.session.flush()

    today = date.today()

    p1 = Project(
        name="Rediseno del portal de clientes",
        description="Nueva experiencia de usuario y migracion a componentes reutilizables.",
        status=ProjectStatus.ACTIVE, priority=Priority.HIGH,
        start_date=today - timedelta(days=20), end_date=today + timedelta(days=40),
        manager=gerente1, team=t_web,
    )
    p2 = Project(
        name="App movil v2",
        description="Rework de la app con modo offline y notificaciones push.",
        status=ProjectStatus.PLANNING, priority=Priority.CRITICAL,
        start_date=today + timedelta(days=5), end_date=today + timedelta(days=90),
        manager=gerente2, team=t_mobile,
    )
    p3 = Project(
        name="Integracion de facturacion",
        description="Conectar con el ERP y automatizar la emision de facturas.",
        status=ProjectStatus.ON_HOLD, priority=Priority.MEDIUM,
        start_date=today - timedelta(days=60), end_date=today - timedelta(days=5),
        manager=gerente1, team=t_web,
    )
    db.session.add_all([p1, p2, p3])
    db.session.flush()

    def mktask(project, title, assignee, status, prio, d_start, d_due, progress=0, deps=None):
        t = Task(
            title=title, project=project, assignee=assignee, status=status, priority=prio,
            start_date=d_start, due_date=d_due, progress=progress, created_by_id=admin.id,
            estimated_hours=16,
        )
        if status == TaskStatus.DONE:
            t.completed_at = datetime.combine(d_due, datetime.min.time())
            t.progress = 100
        if deps:
            t.dependencies = deps
        db.session.add(t)
        return t

    a1 = mktask(p1, "Auditoria UX del portal actual", des1, TaskStatus.DONE, Priority.MEDIUM,
               today - timedelta(days=20), today - timedelta(days=12), 100)
    a2 = mktask(p1, "Wireframes de alta fidelidad", des1, TaskStatus.DONE, Priority.HIGH,
               today - timedelta(days=12), today - timedelta(days=4), 100, deps=[a1])
    a3 = mktask(p1, "Sistema de componentes en React", dev2, TaskStatus.IN_PROGRESS, Priority.HIGH,
               today - timedelta(days=4), today + timedelta(days=10), 55, deps=[a2])
    a4 = mktask(p1, "API de perfil de cliente", dev1, TaskStatus.IN_PROGRESS, Priority.HIGH,
               today - timedelta(days=2), today + timedelta(days=8), 30)
    a5 = mktask(p1, "Pruebas end-to-end", qa1, TaskStatus.TODO, Priority.MEDIUM,
               today + timedelta(days=10), today + timedelta(days=25), 0, deps=[a3, a4])
    a6 = mktask(p1, "Corregir bug de login (vencida)", dev1, TaskStatus.IN_PROGRESS, Priority.CRITICAL,
               today - timedelta(days=6), today - timedelta(days=1), 40)

    b1 = mktask(p2, "Definir arquitectura offline-first", gerente2, TaskStatus.TODO, Priority.CRITICAL,
               today + timedelta(days=5), today + timedelta(days=15), 0)
    b2 = mktask(p2, "Prototipo de sincronizacion", dev2, TaskStatus.TODO, Priority.HIGH,
               today + timedelta(days=15), today + timedelta(days=35), 0, deps=[b1])

    c1 = mktask(p3, "Mapa de campos ERP <-> sistema", dev1, TaskStatus.DONE, Priority.MEDIUM,
               today - timedelta(days=60), today - timedelta(days=45), 100)
    c2 = mktask(p3, "Cliente HTTP del ERP", dev1, TaskStatus.REVIEW, Priority.MEDIUM,
               today - timedelta(days=44), today - timedelta(days=10), 80, deps=[c1])

    db.session.flush()
    db.session.add_all([
        Comment(task=a3, author=dev2, body="Avanzando con los formularios, faltan estados de error."),
        Comment(task=a3, author=gerente1, body="Prioriza el datepicker, lo necesita el equipo de API."),
        Comment(task=a6, author=dev1, body="El bug depende de la nueva libreria de auth, investigando."),
    ])

    db.session.commit()
    print("Seed completo.")
    print("  Admin:    admin@demo.com   / Demo1234")
    print("  Gerente:  gerente@demo.com / Demo1234")
    print("  Colab.:   diego@demo.com   / Demo1234")
