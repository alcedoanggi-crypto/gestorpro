"""Generacion y consulta de notificaciones."""
from datetime import date, timedelta

from flask import current_app

from ..extensions import db
from ..models import Notification, Task
from ..models.enums import TaskStatus


def notify(user, message, link=None, category="info", dedup_key=None):
    if dedup_key and Notification.query.filter_by(user_id=user.id, dedup_key=dedup_key).first():
        return None
    n = Notification(
        user_id=user.id, message=message, link=link, category=category, dedup_key=dedup_key
    )
    db.session.add(n)
    return n


def unread_count(user):
    return Notification.query.filter_by(user_id=user.id, is_read=False).count()


def mark_read(user, notification_id=None):
    q = Notification.query.filter_by(user_id=user.id, is_read=False)
    if notification_id:
        q = q.filter_by(id=notification_id)
    updated = q.update({Notification.is_read: True})
    db.session.commit()
    return updated


def scan_due_soon():
    """Crea notificaciones para tareas por vencer o vencidas. Ideal para un cron."""
    window = current_app.config.get("TASK_DUE_SOON_DAYS", 3)
    today = date.today()
    limit = today + timedelta(days=window)
    created = 0

    tasks = (
        Task.query.filter(
            Task.status != TaskStatus.DONE,
            Task.assignee_id.isnot(None),
            Task.due_date.isnot(None),
            Task.due_date <= limit,
        ).all()
    )
    for t in tasks:
        overdue = t.due_date < today
        key = f"due:{t.id}:{'overdue' if overdue else t.due_date.isoformat()}"
        msg = (
            f"La tarea '{t.title}' esta vencida ({t.due_date:%d/%m})"
            if overdue
            else f"La tarea '{t.title}' vence el {t.due_date:%d/%m}"
        )
        n = notify(
            t.assignee,
            msg,
            link=f"/tareas/{t.id}",
            category="danger" if overdue else "warning",
            dedup_key=key,
        )
        if n is not None:
            created += 1
    db.session.commit()
    return created
