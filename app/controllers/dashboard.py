"""Dashboard principal con tarjetas resumen y graficos."""
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..models import Task
from ..models.enums import TaskStatus
from ..services import report_service
from ..utils.scope import projects_for, tasks_for

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    projects = projects_for(current_user).all()
    tasks = tasks_for(current_user).all()

    stats = report_service.dashboard_stats(projects, tasks)
    charts = {
        "progress": report_service.project_progress_chart(projects),
        "status": report_service.task_status_chart(tasks),
        "monthly": report_service.monthly_completion_chart(tasks),
    }

    my_open_tasks = (
        Task.query.filter(
            Task.assignee_id == current_user.id, Task.status != TaskStatus.DONE
        )
        .order_by(Task.due_date.is_(None), Task.due_date.asc())
        .limit(8)
        .all()
    )
    recent_projects = sorted(projects, key=lambda p: p.created_at, reverse=True)[:5]
    delayed = [t for t in tasks if t.is_overdue][:8]

    return render_template(
        "dashboard/index.html",
        stats=stats,
        charts=charts,
        my_open_tasks=my_open_tasks,
        recent_projects=recent_projects,
        delayed=delayed,
    )
