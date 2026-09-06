"""Modulo de reportes: graficos + exportacion a Excel / PDF."""
from datetime import datetime

from flask import Blueprint, render_template, request, send_file
from flask_login import current_user

from ..models import Task
from ..models.enums import ProjectStatus
from ..services import export_service, report_service
from ..utils.decorators import manager_required
from ..utils.scope import projects_for, tasks_for

reports_bp = Blueprint("reports", __name__)


def _dataset():
    projects = projects_for(current_user).all()
    status = request.args.get("status", "")
    if status in ProjectStatus.ALL:
        projects = [p for p in projects if p.status == status]
    project_ids = {p.id for p in projects}
    tasks = [t for t in tasks_for(current_user).all() if t.project_id in project_ids]
    return projects, tasks


@reports_bp.route("/")
@manager_required
def index():
    projects, tasks = _dataset()
    stats = report_service.dashboard_stats(projects, tasks)
    charts = report_service.build_report_bundle(projects, tasks)
    return render_template(
        "reports/index.html",
        stats=stats, charts=charts, projects=projects,
        status=request.args.get("status", ""),
    )


@reports_bp.route("/export/excel")
@manager_required
def export_excel():
    projects, _ = _dataset()
    buf = export_service.projects_to_excel(projects)
    name = f"reporte_proyectos_{datetime.now():%Y%m%d_%H%M}.xlsx"
    return send_file(
        buf, as_attachment=True, download_name=name,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@reports_bp.route("/export/pdf")
@manager_required
def export_pdf():
    projects, tasks = _dataset()
    stats = report_service.dashboard_stats(projects, tasks)
    buf = export_service.report_to_pdf(projects, stats)
    name = f"reporte_proyectos_{datetime.now():%Y%m%d_%H%M}.pdf"
    return send_file(buf, as_attachment=True, download_name=name, mimetype="application/pdf")
