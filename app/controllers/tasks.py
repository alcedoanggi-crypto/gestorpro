"""CRUD de tareas, cambio rapido de estado y comentarios."""
from datetime import datetime

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from ..extensions import db
from ..forms.task_forms import QuickCommentForm, TaskForm
from ..models import Comment, Project, Task, User
from ..models.enums import TaskStatus
from ..services.notification_service import notify
from ..utils.http import modal_form, modal_success
from ..utils.permissions import (can_edit_task, can_manage_task,
                                 can_view_project)
from ..utils.scope import projects_for, tasks_for

tasks_bp = Blueprint("tasks", __name__)


def _editable_projects():
    return projects_for(current_user).order_by(Project.name).all()


def _populate_choices(form):
    projects = _editable_projects()
    form.project_id.choices = [(p.id, p.name) for p in projects]
    users = User.query.filter(User.active.is_(True)).order_by(User.name).all()
    form.assignee_id.choices = [(0, "— Sin asignar —")] + [(u.id, u.name) for u in users]
    task_opts = Task.query.order_by(Task.title).all()
    form.dependencies.choices = [(t.id, f"{t.title} ({t.project.name})") for t in task_opts]


@tasks_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    project_id = request.args.get("project", type=int)
    mine = request.args.get("mias") == "1"

    query = tasks_for(current_user)
    if mine:
        query = query.filter(Task.assignee_id == current_user.id)
    if status in TaskStatus.ALL:
        query = query.filter(Task.status == status)
    if project_id:
        query = query.filter(Task.project_id == project_id)

    pagination = query.order_by(
        Task.due_date.is_(None), Task.due_date.asc()
    ).paginate(page=page, per_page=15, error_out=False)

    projects = projects_for(current_user).order_by(Project.name).all()
    return render_template(
        "tasks/index.html", pagination=pagination, projects=projects,
        status=status, project_id=project_id, mine=mine,
    )


@tasks_bp.route("/<int:task_id>", methods=["GET", "POST"])
@login_required
def detail(task_id):
    task = Task.query.get_or_404(task_id)
    if not can_view_project(current_user, task.project):
        abort(403)

    form = QuickCommentForm()
    if form.validate_on_submit():
        db.session.add(Comment(body=form.body.data, task_id=task.id, user_id=current_user.id))
        # avisar al responsable si comenta otra persona
        if task.assignee_id and task.assignee_id != current_user.id:
            notify(task.assignee, f"Nuevo comentario en '{task.title}'",
                   link=url_for("tasks.detail", task_id=task.id))
        db.session.commit()
        flash("Comentario agregado.", "success")
        return redirect(url_for("tasks.detail", task_id=task.id))

    return render_template(
        "tasks/detail.html", task=task, form=form,
        can_edit=can_edit_task(current_user, task),
        can_manage=can_manage_task(current_user, task),
    )


@tasks_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.has_role("admin", "gerente"):
        abort(403)
    form = TaskForm()
    _populate_choices(form)
    preselected = request.args.get("project", type=int)
    if preselected and request.method == "GET":
        form.project_id.data = preselected

    if form.validate_on_submit():
        task = Task(
            title=form.title.data.strip(),
            description=form.description.data,
            project_id=form.project_id.data,
            assignee_id=form.assignee_id.data or None,
            status=form.status.data,
            priority=form.priority.data,
            progress=form.progress.data or 0,
            estimated_hours=float(form.estimated_hours.data) if form.estimated_hours.data else None,
            start_date=form.start_date.data,
            due_date=form.due_date.data,
            created_by_id=current_user.id,
        )
        task.dependencies = Task.query.filter(Task.id.in_(form.dependencies.data or [])).all()
        db.session.add(task)
        if task.assignee_id and task.assignee_id != current_user.id:
            db.session.flush()
            notify(task.assignee, f"Se te asigno la tarea '{task.title}'",
                   link=url_for("tasks.detail", task_id=task.id))
        db.session.commit()
        flash("Tarea creada.", "success")
        return modal_success(url_for("tasks.detail", task_id=task.id))
    return modal_form("tasks/_form_modal.html", form, task=None) \
        or render_template("tasks/form.html", form=form, task=None)


@tasks_bp.route("/<int:task_id>/editar", methods=["GET", "POST"])
@login_required
def edit(task_id):
    task = Task.query.get_or_404(task_id)
    if not can_edit_task(current_user, task):
        abort(403)

    form = TaskForm(obj=task)
    _populate_choices(form)
    if form.validate_on_submit():
        prev_assignee = task.assignee_id
        form.populate_obj(task)
        task.assignee_id = form.assignee_id.data or None
        task.estimated_hours = float(form.estimated_hours.data) if form.estimated_hours.data else None
        task.dependencies = Task.query.filter(
            Task.id.in_(form.dependencies.data or []), Task.id != task.id
        ).all()
        if task.status == TaskStatus.DONE and not task.completed_at:
            task.completed_at = datetime.utcnow()
            task.progress = 100
        if task.status != TaskStatus.DONE:
            task.completed_at = None
        if task.assignee_id and task.assignee_id != prev_assignee:
            notify(task.assignee, f"Se te asigno la tarea '{task.title}'",
                   link=url_for("tasks.detail", task_id=task.id))
        db.session.commit()
        flash("Tarea actualizada.", "success")
        return modal_success(url_for("tasks.detail", task_id=task.id))

    if request.method == "GET":
        form.assignee_id.data = task.assignee_id or 0
        form.dependencies.data = [d.id for d in task.dependencies]
    return modal_form("tasks/_form_modal.html", form, task=task) \
        or render_template("tasks/form.html", form=form, task=task)


@tasks_bp.route("/<int:task_id>/estado", methods=["POST"])
@login_required
def change_status(task_id):
    task = Task.query.get_or_404(task_id)
    if not can_edit_task(current_user, task):
        abort(403)
    new_status = request.form.get("status")
    if new_status not in TaskStatus.ALL:
        abort(400)
    task.status = new_status
    if new_status == TaskStatus.DONE:
        task.mark_done()
    else:
        task.completed_at = None
    db.session.commit()
    flash("Estado actualizado.", "success")
    return redirect(request.referrer or url_for("tasks.detail", task_id=task.id))


@tasks_bp.route("/<int:task_id>/eliminar", methods=["POST"])
@login_required
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    if not can_manage_task(current_user, task):
        abort(403)
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    flash("Tarea eliminada.", "info")
    return modal_success(url_for("projects.detail", project_id=project_id))
