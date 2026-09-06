import secrets
from datetime import datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db
from .role import Role

# Relacion N:M usuarios <-> equipos
team_members = db.Table(
    "team_members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("team_id", db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    job_title = db.Column(db.String(120))
    avatar_url = db.Column(db.String(255))
    active = db.Column("is_active", db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)

    reset_token = db.Column(db.String(255), index=True)
    reset_token_expiry = db.Column(db.DateTime)

    role = db.relationship("Role", back_populates="users")
    teams = db.relationship("Team", secondary=team_members, back_populates="members")
    managed_projects = db.relationship(
        "Project", back_populates="manager", foreign_keys="Project.manager_id"
    )
    assigned_tasks = db.relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Notification.created_at.desc()",
    )

    # --- Contrasena ---
    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    # --- Roles ---
    @property
    def role_name(self):
        return self.role.name if self.role else None

    def has_role(self, *names):
        return self.role_name in names

    @property
    def is_admin(self):
        return self.role_name == Role.ADMIN

    @property
    def is_manager(self):
        return self.role_name == Role.MANAGER

    # Flask-Login usa esta propiedad para permitir el acceso
    @property
    def is_active(self):
        return bool(self.active)

    # --- Recuperacion de contrasena ---
    def generate_reset_token(self, ttl_hours=1):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=ttl_hours)
        return self.reset_token

    def verify_reset_token(self, token):
        return bool(
            self.reset_token
            and token
            and secrets.compare_digest(self.reset_token, token)
            and self.reset_token_expiry
            and self.reset_token_expiry > datetime.utcnow()
        )

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None

    # --- Presentacion ---
    @property
    def initials(self):
        parts = [p for p in self.name.split() if p]
        return ("".join(p[0] for p in parts[:2]) or "?").upper()

    def __repr__(self):
        return f"<User {self.email}>"
