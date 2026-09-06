"""Consultas filtradas segun el rol del usuario autenticado."""
from ..extensions import db
from ..models import Project, Task, Team, User


def projects_for(user):
    q = Project.query
    if user.is_admin:
        return q
    if user.is_manager:
        return q.filter(Project.manager_id == user.id)
    return q.filter(
        db.or_(
            Project.tasks.any(Task.assignee_id == user.id),
            Project.team.has(Team.members.any(User.id == user.id)),
        )
    )


def tasks_for(user):
    q = Task.query
    if user.is_admin:
        return q
    if user.is_manager:
        return q.join(Project).filter(Project.manager_id == user.id)
    return q.filter(Task.assignee_id == user.id)


def visible_project_ids(user):
    return [p.id for p in projects_for(user).with_entities(Project.id).all()]
