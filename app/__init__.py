"""Application factory. Ensambla configuracion, extensiones, blueprints y CLI."""
import os
from datetime import datetime

from flask import Flask, render_template
from flask_login import current_user

from .config import config
from .extensions import csrf, db, login_manager, mail, migrate


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_CONFIG", "default")
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    _init_extensions(app)
    _register_blueprints(app)
    _register_jinja(app)
    _register_context(app)
    _register_errors(app)
    _register_cli(app)
    return app


def _init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


def _register_blueprints(app):
    from .controllers.api import api_bp
    from .controllers.auth import auth_bp
    from .controllers.dashboard import dashboard_bp
    from .controllers.projects import projects_bp
    from .controllers.reports import reports_bp
    from .controllers.tasks import tasks_bp
    from .controllers.teams import teams_bp
    from .controllers.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp, url_prefix="/proyectos")
    app.register_blueprint(tasks_bp, url_prefix="/tareas")
    app.register_blueprint(users_bp, url_prefix="/usuarios")
    app.register_blueprint(teams_bp, url_prefix="/equipos")
    app.register_blueprint(reports_bp, url_prefix="/reportes")
    app.register_blueprint(api_bp, url_prefix="/api")
    csrf.exempt(api_bp)  # las llamadas JSON usan sesion + header propio


def _register_jinja(app):
    from .models.enums import Priority, ProjectStatus, TaskStatus

    colors = {
        ProjectStatus.ACTIVE: "success", ProjectStatus.PLANNING: "info",
        ProjectStatus.ON_HOLD: "warning", ProjectStatus.COMPLETED: "secondary",
        ProjectStatus.CANCELLED: "danger",
        TaskStatus.TODO: "secondary", TaskStatus.IN_PROGRESS: "primary",
        TaskStatus.REVIEW: "warning", TaskStatus.DONE: "success",
        Priority.LOW: "success", Priority.MEDIUM: "info",
        Priority.HIGH: "warning", Priority.CRITICAL: "danger",
    }

    @app.template_filter("fecha")
    def _fecha(value, fmt="%d/%m/%Y"):
        return value.strftime(fmt) if value else "—"

    @app.template_filter("desde")
    def _desde(value):
        if not value:
            return ""
        delta = datetime.utcnow() - value
        s = delta.total_seconds()
        if s < 60:
            return "hace instantes"
        if s < 3600:
            return f"hace {int(s // 60)} min"
        if s < 86400:
            return f"hace {int(s // 3600)} h"
        return f"hace {delta.days} d"

    app.jinja_env.globals.update(
        bcolor=lambda key: colors.get(key, "secondary"),
        ProjectStatus=ProjectStatus,
        TaskStatus=TaskStatus,
        Priority=Priority,
    )


def _register_context(app):
    from .services.notification_service import unread_count

    @app.context_processor
    def inject_globals():
        ctx = {"now": datetime.utcnow(), "nav_notifications": [], "nav_unread": 0}
        if current_user.is_authenticated:
            try:
                ctx["nav_notifications"] = current_user.notifications[:8]
                ctx["nav_unread"] = unread_count(current_user)
            except Exception:  # p. ej. sesion de BD rota durante un error 500
                db.session.rollback()
        return ctx


def _register_errors(app):
    for code in (403, 404, 500):
        app.register_error_handler(
            code,
            lambda e, code=code: (render_template(f"errors/{code}.html"), code),
        )


def _register_cli(app):
    from .models import Role
    from .seeds import run_seed
    from .services.notification_service import scan_due_soon

    @app.cli.command("init-db")
    def init_db():
        """Crea las tablas y los roles base."""
        db.create_all()
        Role.seed_defaults()
        print("Base de datos lista.")

    @app.cli.command("seed")
    def seed():
        """Carga datos de demostracion."""
        run_seed()

    @app.cli.command("scan-notifications")
    def scan_notifications():
        """Genera notificaciones de tareas por vencer (usar en cron)."""
        print(f"{scan_due_soon()} notificaciones generadas.")
