"""Helpers para servir formularios en modal (AJAX) o pagina completa (fallback)."""
from flask import flash, jsonify, redirect, render_template, request


def wants_json():
    """True cuando la vista debe responder JSON / fragmento en vez de pagina completa.

    Lo activan las peticiones AJAX de los modales (cabecera ``X-Requested-With``)
    o un ``Accept: application/json`` explicito.
    """
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True
    accept = request.accept_mimetypes
    return bool(accept.accept_json and not accept.accept_html)


def modal_success(redirect_url):
    """Exito al guardar: JSON con destino si es AJAX, redirect normal si no."""
    if wants_json():
        return jsonify(ok=True, redirect=redirect_url)
    return redirect(redirect_url)


def modal_blocked(message, redirect_url):
    """Accion no permitida (p. ej. eliminar con dependencias)."""
    if wants_json():
        return jsonify(ok=False, error=message)
    flash(message, "danger")
    return redirect(redirect_url)


def modal_form(template, form, **context):
    """Fragmento del formulario para el modal (GET) o con errores (POST invalido).

    Devuelve ``None`` cuando la peticion NO es AJAX, para que la vista haga el
    render de la pagina completa como siempre.
    """
    if wants_json():
        status = 422 if form.errors else 200
        return render_template(template, form=form, **context), status
    return None
