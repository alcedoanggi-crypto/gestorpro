from datetime import datetime, date

from ..extensions import db
from .enums import TaskStatus, Priority

# Dependencias entre tareas (para el diagrama de Gantt)
task_dependencies = db.Table(
    "task_dependencies",
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    db.Column("depends_on_id", db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default=TaskStatus.TODO, nullable=False, index=True)
    priority = db.Column(db.String(20), default=Priority.MEDIUM, nullable=False)
    progress = db.Column(db.Integer, default=0, nullable=False)
    estimated_hours = db.Column(db.Float)
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date, index=True)
    completed_at = db.Column(db.DateTime)

    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    project = db.relationship("Project", back_populates="tasks")
    assignee = db.relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    creator = db.relationship("User", foreign_keys=[created_by_id])
    comments = db.relationship(
        "Comment", back_populates="task", cascade="all, delete-orphan", order_by="Comment.created_at"
    )
    dependencies = db.relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin="Task.id == task_dependencies.c.task_id",
        secondaryjoin="Task.id == task_dependencies.c.depends_on_id",
        backref="dependents",
    )

    # --- Estado temporal ---
    @property
    def is_overdue(self):
        return bool(self.due_date and self.due_date < date.today() and self.status != TaskStatus.DONE)

    @property
    def days_to_due(self):
        return (self.due_date - date.today()).days if self.due_date else None

    def is_due_soon(self, window=3):
        d = self.days_to_due
        return d is not None and 0 <= d <= window and self.status != TaskStatus.DONE

    @property
    def status_label(self):
        return TaskStatus.LABELS.get(self.status, self.status)

    @property
    def priority_label(self):
        return Priority.LABELS.get(self.priority, self.priority)

    def mark_done(self):
        self.status = TaskStatus.DONE
        self.progress = 100
        self.completed_at = datetime.utcnow()

    # --- Serializacion para Frappe Gantt ---
    def to_gantt(self):
        start = self.start_date or self.due_date or date.today()
        end = self.due_date or self.start_date or date.today()
        if end < start:
            end = start
        return {
            "id": str(self.id),
            "name": self.title,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "progress": self.progress or 0,
            "dependencies": ",".join(str(d.id) for d in self.dependencies),
            "custom_class": f"bar-{self.status}",
        }

    def __repr__(self):
        return f"<Task {self.title!r}>"
