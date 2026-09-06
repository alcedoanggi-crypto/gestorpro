"""Agregaciones para el dashboard y el modulo de reportes.

Devuelve estructuras listas para Chart.js: {labels: [...], datasets: [...]}.
"""
from collections import Counter, defaultdict
from datetime import date

from ..models import Project, Task, User
from ..models.enums import ProjectStatus, TaskStatus, Priority

PALETTE = ["#2563eb", "#7c3aed", "#10b981", "#f97316", "#ef4444", "#0ea5e9", "#ec4899"]


def dashboard_stats(projects, tasks):
    today = date.today()
    return {
        "total_projects": len(projects),
        "active_projects": sum(1 for p in projects if p.status == ProjectStatus.ACTIVE),
        "delayed_projects": sum(1 for p in projects if p.is_delayed),
        "total_tasks": len(tasks),
        "pending_tasks": sum(1 for t in tasks if t.status != TaskStatus.DONE),
        "overdue_tasks": sum(1 for t in tasks if t.is_overdue),
        "due_soon_tasks": sum(1 for t in tasks if t.is_due_soon()),
        "done_tasks": sum(1 for t in tasks if t.status == TaskStatus.DONE),
    }


def project_progress_chart(projects):
    projects = sorted(projects, key=lambda p: p.progress, reverse=True)[:12]
    return {
        "labels": [p.name for p in projects],
        "datasets": [{
            "label": "% completado",
            "data": [p.progress for p in projects],
            "backgroundColor": PALETTE[0],
        }],
    }


def task_status_chart(tasks):
    counts = Counter(t.status for t in tasks)
    labels = [TaskStatus.LABELS[s] for s in TaskStatus.ALL]
    return {
        "labels": labels,
        "datasets": [{
            "data": [counts.get(s, 0) for s in TaskStatus.ALL],
            "backgroundColor": PALETTE[:4],
        }],
    }


def workload_chart(tasks):
    """Tareas abiertas por usuario asignado."""
    by_user = defaultdict(int)
    for t in tasks:
        if t.status != TaskStatus.DONE and t.assignee:
            by_user[t.assignee.name] += 1
    items = sorted(by_user.items(), key=lambda kv: kv[1], reverse=True)[:12]
    return {
        "labels": [name for name, _ in items],
        "datasets": [{
            "label": "Tareas abiertas",
            "data": [n for _, n in items],
            "backgroundColor": PALETTE[1],
        }],
    }


def deadline_compliance_chart(tasks):
    """Cumplimiento de plazos sobre tareas completadas."""
    on_time = late = 0
    for t in tasks:
        if t.status == TaskStatus.DONE and t.due_date and t.completed_at:
            if t.completed_at.date() <= t.due_date:
                on_time += 1
            else:
                late += 1
    pending_overdue = sum(1 for t in tasks if t.is_overdue)
    return {
        "labels": ["A tiempo", "Con retraso", "Vencidas sin cerrar"],
        "datasets": [{
            "data": [on_time, late, pending_overdue],
            "backgroundColor": [PALETTE[2], PALETTE[3], PALETTE[4]],
        }],
    }


def priority_distribution_chart(tasks):
    counts = Counter(t.priority for t in tasks if t.status != TaskStatus.DONE)
    return {
        "labels": [Priority.LABELS[p] for p in Priority.ALL],
        "datasets": [{
            "data": [counts.get(p, 0) for p in Priority.ALL],
            "backgroundColor": [PALETTE[2], PALETTE[1], PALETTE[3], PALETTE[4]],
        }],
    }


def monthly_completion_chart(tasks):
    """Serie de tareas completadas por mes (ultimos 6 meses)."""
    from datetime import date as _d

    today = _d.today()
    months = []
    for i in range(5, -1, -1):
        y = today.year + (today.month - 1 - i) // 12
        m = (today.month - 1 - i) % 12 + 1
        months.append((y, m))
    counts = {ym: 0 for ym in months}
    for t in tasks:
        if t.status == TaskStatus.DONE and t.completed_at:
            ym = (t.completed_at.year, t.completed_at.month)
            if ym in counts:
                counts[ym] += 1
    labels = [f"{m:02d}/{y}" for y, m in months]
    return {
        "labels": labels,
        "datasets": [{
            "label": "Tareas completadas",
            "data": [counts[ym] for ym in months],
            "borderColor": PALETTE[0],
            "backgroundColor": "rgba(37,99,235,.15)",
            "fill": True,
            "tension": 0.35,
        }],
    }


def build_report_bundle(projects, tasks):
    return {
        "progress": project_progress_chart(projects),
        "status": task_status_chart(tasks),
        "workload": workload_chart(tasks),
        "compliance": deadline_compliance_chart(tasks),
        "priority": priority_distribution_chart(tasks),
        "monthly": monthly_completion_chart(tasks),
    }
