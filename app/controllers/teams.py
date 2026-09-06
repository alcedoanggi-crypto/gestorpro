"""Gestion de equipos (admin y gerentes)."""
from flask import Blueprint, flash, render_template, request, url_for

from ..extensions import db
from ..forms.team_forms import TeamForm
from ..models import Team, User
from ..utils.decorators import manager_required
from ..utils.http import modal_blocked, modal_form, modal_success

teams_bp = Blueprint("teams", __name__)


def _member_choices(form):
    users = User.query.filter(User.active.is_(True)).order_by(User.name).all()
    form.member_ids.choices = [(u.id, f"{u.name} ({u.role.name})") for u in users]


@teams_bp.route("/")
@manager_required
def index():
    teams = Team.query.order_by(Team.name).all()
    return render_template("teams/index.html", teams=teams)


@teams_bp.route("/nuevo", methods=["GET", "POST"])
@manager_required
def create():
    form = TeamForm()
    _member_choices(form)
    if form.validate_on_submit():
        team = Team(name=form.name.data.strip(), description=form.description.data)
        team.members = User.query.filter(User.id.in_(form.member_ids.data or [])).all()
        db.session.add(team)
        db.session.commit()
        flash("Equipo creado.", "success")
        return modal_success(url_for("teams.index"))
    return modal_form("teams/_form_modal.html", form, team=None) \
        or render_template("teams/form.html", form=form, team=None)


@teams_bp.route("/<int:team_id>/editar", methods=["GET", "POST"])
@manager_required
def edit(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamForm(obj=team)
    _member_choices(form)
    if form.validate_on_submit():
        team.name = form.name.data.strip()
        team.description = form.description.data
        team.members = User.query.filter(User.id.in_(form.member_ids.data or [])).all()
        db.session.commit()
        flash("Equipo actualizado.", "success")
        return modal_success(url_for("teams.index"))
    if request.method == "GET":
        form.member_ids.data = [u.id for u in team.members]
    return modal_form("teams/_form_modal.html", form, team=team) \
        or render_template("teams/form.html", form=form, team=team)


@teams_bp.route("/<int:team_id>/eliminar", methods=["POST"])
@manager_required
def delete(team_id):
    team = Team.query.get_or_404(team_id)
    if team.projects:
        return modal_blocked("El equipo tiene proyectos asociados.",
                             url_for("teams.index"))
    db.session.delete(team)
    db.session.commit()
    flash("Equipo eliminado.", "info")
    return modal_success(url_for("teams.index"))
