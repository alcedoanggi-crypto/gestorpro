"""Endpoints JSON para el Gantt interactivo y las notificaciones."""
from datetime import date, datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Project, Task
from ..models.enums import TaskStatus
from ..services.notification_service import mark_read
from ..utils.permissions import can_edit_task, can_view_project

api_bp = Blueprint("api", __name__)


@api_bp.before_request
@login_required
def _guard():
    """Todas las rutas del API requieren sesion activa."""
    return None


def _parse_date(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "")[:19]).date()


@api_bp.get("/projects/<int:project_id>/gantt")
def project_gantt(project_id):
    project = Project.query.get_or_404(project_id)
    if not can_view_project(current_user, project):
        return jsonify(error="forbidden"), 403
    return jsonify(tasks=[t.to_gantt() for t in project.tasks])


@api_bp.post("/tasks/<int:task_id>/schedule")
def reschedule_task(task_id):
    """Persiste el arrastrar/soltar de fechas desde Frappe Gantt."""
    task = Task.query.get_or_404(task_id)
    if not can_edit_task(current_user, task):
        return jsonify(error="forbidden"), 403
    data = request.get_json(silent=True) or {}
    try:
        start = _parse_date(data.get("start"))
        end = _parse_date(data.get("end"))
    except ValueError:
        return jsonify(error="invalid_date"), 400
    if start:
        task.start_date = start
    if end:
        task.due_date = end
    db.session.commit()
    return jsonify(ok=True, task=task.to_gantt())


@api_bp.post("/tasks/<int:task_id>/progress")
def update_progress(task_id):
    task = Task.query.get_or_404(task_id)
    if not can_edit_task(current_user, task):
        return jsonify(error="forbidden"), 403
    data = request.get_json(silent=True) or {}
    try:
        progress = max(0, min(100, int(data.get("progress", task.progress))))
    except (TypeError, ValueError):
        return jsonify(error="invalid"), 400
    task.progress = progress
    if progress == 100 and task.status != TaskStatus.DONE:
        task.mark_done()
    db.session.commit()
    return jsonify(ok=True, progress=task.progress, status=task.status)


@api_bp.get("/notifications")
def notifications():
    items = current_user.notifications[:20]
    return jsonify(
        unread=sum(1 for n in current_user.notifications if not n.is_read),
        items=[
            {
                "id": n.id, "message": n.message, "link": n.link,
                "category": n.category, "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in items
        ],
    )


@api_bp.post("/notifications/read")
def read_notifications():
    data = request.get_json(silent=True) or {}
    count = mark_read(current_user, data.get("id"))
    return jsonify(ok=True, marked=count)
