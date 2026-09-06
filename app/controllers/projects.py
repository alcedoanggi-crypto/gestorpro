"""CRUD de proyectos + vista de cronograma (Gantt)."""
import re
from datetime import datetime

from flask import (Blueprint, abort, flash, render_template, request,
                   send_file, url_for)
from flask_login import current_user, login_required

from ..extensions import db
from ..forms.project_forms import ProjectForm
from ..models import Project, Role, Team, User
from ..models.enums import ProjectStatus
from ..services import export_service
from ..utils.decorators import manager_required
from ..utils.http import modal_form, modal_success
from ..utils.permissions import (can_delete_project, can_edit_project,
                                 can_view_project)
from ..utils.scope import projects_for

projects_bp = Blueprint("projects", __name__)


def _populate_choices(form):
    managers = User.query.join(Role).filter(
        Role.name.in_([Role.ADMIN, Role.MANAGER]), User.active.is_(True)
    ).order_by(User.name).all()
    form.manager_id.choices = [(0, "— Sin asignar —")] + [(u.id, u.name) for u in managers]
    form.team_id.choices = [(0, "— Sin equipo —")] + [
        (t.id, t.name) for t in Team.query.order_by(Team.name).all()
    ]


@projects_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    q = request.args.get("q", "").strip()

    query = projects_for(current_user)
    if status in ProjectStatus.ALL:
        query = query.filter(Project.status == status)
    if q:
        query = query.filter(Project.name.ilike(f"%{q}%"))

    pagination = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template(
        "projects/index.html", pagination=pagination, status=status, q=q
    )


@projects_bp.route("/<int:project_id>")
@login_required
def detail(project_id):
    project = Project.query.get_or_404(project_id)
    if not can_view_project(current_user, project):
        abort(403)
    gantt_tasks = [t.to_gantt() for t in project.tasks]
    return render_template(
        "projects/detail.html",
        project=project,
        gantt_tasks=gantt_tasks,
        can_edit=can_edit_project(current_user, project),
    )


@projects_bp.route("/<int:project_id>/gantt.pdf")
@login_required
def gantt_pdf(project_id):
    project = Project.query.get_or_404(project_id)
    if not can_view_project(current_user, project):
        abort(403)
    buf = export_service.project_gantt_to_pdf(project)
    slug = re.sub(r"[^\w\-]+", "_", project.name).strip("_") or "proyecto"
    name = f"cronograma_{slug}_{datetime.now():%Y%m%d}.pdf"
    return send_file(buf, as_attachment=True, download_name=name,
                     mimetype="application/pdf")


@projects_bp.route("/nuevo", methods=["GET", "POST"])
@manager_required
def create():
    form = ProjectForm()
    _populate_choices(form)
    if form.validate_on_submit():
        project = Project(
            name=form.name.data.strip(),
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            manager_id=form.manager_id.data or None,
            team_id=form.team_id.data or None,
        )
        if not project.manager_id and current_user.is_manager:
            project.manager_id = current_user.id
        db.session.add(project)
        db.session.commit()
        flash("Proyecto creado.", "success")
        return modal_success(url_for("projects.detail", project_id=project.id))
    return modal_form("projects/_form_modal.html", form, project=None) \
        or render_template("projects/form.html", form=form, project=None)


@projects_bp.route("/<int:project_id>/editar", methods=["GET", "POST"])
@login_required
def edit(project_id):
    project = Project.query.get_or_404(project_id)
    if not can_edit_project(current_user, project):
        abort(403)

    form = ProjectForm(obj=project)
    _populate_choices(form)
    if form.validate_on_submit():
        form.populate_obj(project)
        project.manager_id = form.manager_id.data or None
        project.team_id = form.team_id.data or None
        db.session.commit()
        flash("Proyecto actualizado.", "success")
        return modal_success(url_for("projects.detail", project_id=project.id))

    if request.method == "GET":
        form.manager_id.data = project.manager_id or 0
        form.team_id.data = project.team_id or 0
    return modal_form("projects/_form_modal.html", form, project=project) \
        or render_template("projects/form.html", form=form, project=project)


@projects_bp.route("/<int:project_id>/eliminar", methods=["POST"])
@login_required
def delete(project_id):
    project = Project.query.get_or_404(project_id)
    if not can_delete_project(current_user, project):
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash("Proyecto eliminado.", "info")
    return modal_success(url_for("projects.index"))
