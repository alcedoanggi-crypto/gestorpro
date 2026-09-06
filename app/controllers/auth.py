"""Autenticacion: login, registro, logout y recuperacion de contrasena."""
from datetime import datetime

from flask import (Blueprint, flash, redirect, render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..forms.auth_forms import (ForgotPasswordForm, LoginForm, RegisterForm,
                                ResetPasswordForm)
from ..models import Role, User
from ..services.mail_service import send_password_reset_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Tu cuenta esta desactivada. Contacta al administrador.", "danger")
                return redirect(url_for("auth.login"))
            login_user(user, remember=form.remember.data)
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            nxt = request.args.get("next")
            if nxt and nxt.startswith("/"):
                return redirect(nxt)
            return redirect(url_for("dashboard.index"))
        flash("Correo o contrasena incorrectos.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/registro", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese correo.", "warning")
            return render_template("auth/register.html", form=form)

        # El primer usuario del sistema es administrador; el resto, colaboradores.
        first = User.query.count() == 0
        role = Role.get(Role.ADMIN if first else Role.COLLABORATOR)
        user = User(name=form.name.data.strip(), email=email, role=role)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Cuenta creada correctamente. Ya puedes iniciar sesion.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesion cerrada.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/recuperar", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            token = user.generate_reset_token(ttl_hours=1)
            db.session.commit()
            send_password_reset_email(user, token)
        # Respuesta identica exista o no el correo (evita enumeracion de usuarios)
        flash("Si el correo existe, enviamos un enlace para restablecer la contrasena.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/restablecer/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash("El enlace es invalido o ha expirado.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()
        flash("Contrasena actualizada. Inicia sesion.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)
