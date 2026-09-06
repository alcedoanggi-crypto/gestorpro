from datetime import datetime, date

from ..extensions import db
from .enums import ProjectStatus, Priority, TaskStatus


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default=ProjectStatus.PLANNING, nullable=False, index=True)
    priority = db.Column(db.String(20), default=Priority.MEDIUM, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    manager = db.relationship("User", back_populates="managed_projects", foreign_keys=[manager_id])
    team = db.relationship("Team", back_populates="projects")
    tasks = db.relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Task.start_date",
    )

    # --- Metricas derivadas ---
    @property
    def progress(self):
        if not self.tasks:
            return 0
        done = sum(1 for t in self.tasks if t.status == TaskStatus.DONE)
        return round(done / len(self.tasks) * 100)

    @property
    def task_count(self):
        return len(self.tasks)

    @property
    def open_task_count(self):
        return sum(1 for t in self.tasks if t.status != TaskStatus.DONE)

    @property
    def overdue_task_count(self):
        return sum(1 for t in self.tasks if t.is_overdue)

    @property
    def is_delayed(self):
        return (
            self.end_date is not None
            and self.end_date < date.today()
            and self.status not in ProjectStatus.CLOSED
        )

    @property
    def status_label(self):
        return ProjectStatus.LABELS.get(self.status, self.status)

    @property
    def priority_label(self):
        return Priority.LABELS.get(self.priority, self.priority)

    def __repr__(self):
        return f"<Project {self.name}>"
