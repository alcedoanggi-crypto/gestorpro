"""Envio de correo. Si SMTP no esta configurado, se registra en consola."""
from flask import current_app, render_template, url_for
from flask_mail import Message

from ..extensions import mail


def _send(subject, recipients, body_text, body_html=None):
    app = current_app._get_current_object()
    if not app.config.get("MAIL_USERNAME") and not app.config.get("TESTING"):
        app.logger.warning("MAIL no configurado. Correo a %s:\n%s", recipients, body_text)
        return False
    msg = Message(subject=subject, recipients=recipients, body=body_text, html=body_html)
    try:
        mail.send(msg)
        return True
    except Exception as exc:  # pragma: no cover - depende del entorno SMTP
        app.logger.error("Fallo al enviar correo: %s", exc)
        return False


def send_password_reset_email(user, token):
    link = url_for("auth.reset_password", token=token, _external=True)
    text = (
        f"Hola {user.name},\n\n"
        f"Solicitaste restablecer tu contrasena en GestorPro.\n"
        f"Abre este enlace (valido 1 hora): {link}\n\n"
        f"Si no fuiste tu, ignora este mensaje."
    )
    html = render_template("auth/email_reset.html", user=user, link=link)
    return _send("Recuperacion de contrasena - GestorPro", [user.email], text, html)
