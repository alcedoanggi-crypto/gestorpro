"""Gestion de usuarios (solo administradores)."""
import secrets

from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from ..extensions import db
from ..forms.user_forms import ProfileForm, UserForm
from ..models import Role, User
from ..utils.decorators import admin_required
from ..utils.http import modal_blocked, modal_form, modal_success

users_bp = Blueprint("users", __name__)


def _role_choices():
    return [(r.id, r.name.capitalize()) for r in Role.query.order_by(Role.name).all()]


@users_bp.route("/")
@admin_required
def index():
    q = request.args.get("q", "").strip()
    query = User.query
    if q:
        query = query.filter(db.or_(User.name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%")))
    users = query.order_by(User.name).all()
    return render_template("users/index.html", users=users, q=q)


@users_bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def create():
    form = UserForm()
    form.role_id.choices = _role_choices()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            form.email.errors.append("Ese correo ya esta registrado.")
        else:
            user = User(
                name=form.name.data.strip(), email=email,
                job_title=form.job_title.data, role_id=form.role_id.data,
                active=form.is_active.data,
            )
            user.set_password(form.password.data or secrets.token_urlsafe(12))
            db.session.add(user)
            db.session.commit()
            flash("Usuario creado.", "success")
            return modal_success(url_for("users.index"))
    return modal_form("users/_form_modal.html", form, user=None) \
        or render_template("users/form.html", form=form, user=None)


@users_bp.route("/<int:user_id>/editar", methods=["GET", "POST"])
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role_id.choices = _role_choices()
    if request.method == "GET":
        form.is_active.data = user.is_active

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        other = User.query.filter(User.email == email, User.id != user.id).first()
        if user.id == current_user.id and not form.is_active.data:
            form.is_active.errors.append("No puedes desactivar tu propia cuenta.")
        elif other:
            form.email.errors.append("Ese correo ya esta en uso.")
        else:
            user.name = form.name.data.strip()
            user.email = email
            user.job_title = form.job_title.data
            user.role_id = form.role_id.data
            user.active = form.is_active.data
            if form.password.data:
                user.set_password(form.password.data)
            db.session.commit()
            flash("Usuario actualizado.", "success")
            return modal_success(url_for("users.index"))
    return modal_form("users/_form_modal.html", form, user=user) \
        or render_template("users/form.html", form=form, user=user)


@users_bp.route("/<int:user_id>/toggle", methods=["POST"])
@admin_required
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return modal_blocked("No puedes desactivar tu propia cuenta.",
                             url_for("users.index"))
    user.active = not user.active
    db.session.commit()
    flash(f"Cuenta {'activada' if user.active else 'desactivada'}.", "info")
    return modal_success(url_for("users.index"))


@users_bp.route("/<int:user_id>/eliminar", methods=["POST"])
@admin_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return modal_blocked("No puedes eliminar tu propia cuenta.",
                             url_for("users.index"))
    if user.managed_projects:
        return modal_blocked("Ese usuario gestiona proyectos. Reasignalos antes de eliminarlo.",
                             url_for("users.index"))
    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado.", "info")
    return modal_success(url_for("users.index"))


# --------------------------------------------------------------------------- #
# Perfil propio (cualquier rol)
# --------------------------------------------------------------------------- #
@users_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data.strip()
        current_user.job_title = form.job_title.data
        current_user.avatar_url = form.avatar_url.data
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data or ""):
                flash("La contrasena actual no es correcta.", "danger")
                return render_template("users/profile.html", form=form)
            current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Perfil actualizado.", "success")
        return redirect(url_for("users.profile"))
    return render_template("users/profile.html", form=form)
