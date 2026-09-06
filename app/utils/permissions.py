"""Reglas de acceso a nivel de objeto."""


def can_view_project(user, project):
    if user.is_admin:
        return True
    if user.is_manager and project.manager_id == user.id:
        return True
    if project.team and user in project.team.members:
        return True
    return any(t.assignee_id == user.id for t in project.tasks)


def can_edit_project(user, project):
    return user.is_admin or (user.is_manager and project.manager_id == user.id)


def can_delete_project(user, project):
    return can_edit_project(user, project)


def can_edit_task(user, task):
    return (
        user.is_admin
        or (user.is_manager and task.project.manager_id == user.id)
        or task.assignee_id == user.id
    )


def can_manage_task(user, task):
    """Crear / borrar / reasignar (no solo cambiar estado)."""
    return user.is_admin or (user.is_manager and task.project.manager_id == user.id)
