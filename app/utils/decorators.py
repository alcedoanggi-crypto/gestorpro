"""Decoradores de autorizacion por rol."""
from functools import wraps

from flask import abort
from flask_login import current_user

from ..models import Role


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)
            return view(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(view):
    return role_required(Role.ADMIN)(view)


def manager_required(view):
    return role_required(Role.ADMIN, Role.MANAGER)(view)
