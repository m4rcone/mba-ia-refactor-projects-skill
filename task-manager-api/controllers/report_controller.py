from collections import defaultdict
from datetime import timedelta

from middlewares.error_handler import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.dates import utcnow

HIGH_PRIORITY_THRESHOLD = 2
RECENT_ACTIVITY_DAYS = 7


def summary_report():
    tasks = Task.get_all()
    users = User.get_all()
    now = utcnow()
    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)

    status_counts = {
        status: 0 for status in ("pending", "in_progress", "done", "cancelled")
    }
    priority_counts = {priority: 0 for priority in range(1, 6)}
    overdue_list = []
    tasks_by_user = defaultdict(list)

    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.priority in priority_counts:
            priority_counts[task.priority] += 1
        if task.is_overdue():
            overdue_list.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": str(task.due_date),
                    "days_overdue": (now - task.due_date).days,
                }
            )
        tasks_by_user[task.user_id].append(task)

    recent_created = sum(
        1 for task in tasks if task.created_at and task.created_at >= since
    )
    recent_done = sum(
        1
        for task in tasks
        if task.status == "done" and task.updated_at and task.updated_at >= since
    )

    user_stats = []
    for user in users:
        user_tasks = tasks_by_user.get(user.id, [])
        total = len(user_tasks)
        completed = sum(1 for task in user_tasks if task.status == "done")
        user_stats.append(
            {
                "user_id": user.id,
                "user_name": user.name,
                "total_tasks": total,
                "completed_tasks": completed,
                "completion_rate": (
                    round((completed / total) * 100, 2) if total > 0 else 0
                ),
            }
        )

    return {
        "generated_at": str(now),
        "overview": {
            "total_tasks": len(tasks),
            "total_users": len(users),
            "total_categories": Category.count(),
        },
        "tasks_by_status": status_counts,
        "tasks_by_priority": {
            "critical": priority_counts[1],
            "high": priority_counts[2],
            "medium": priority_counts[3],
            "low": priority_counts[4],
            "minimal": priority_counts[5],
        },
        "overdue": {
            "count": len(overdue_list),
            "tasks": overdue_list,
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_created,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }


def user_report(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    tasks = Task.get_by_user(user_id)
    total = len(tasks)
    status_counts = {
        status: 0 for status in ("done", "pending", "in_progress", "cancelled")
    }
    overdue = 0
    high_priority = 0

    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.priority <= HIGH_PRIORITY_THRESHOLD:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        "statistics": {
            "total_tasks": total,
            "done": status_counts["done"],
            "pending": status_counts["pending"],
            "in_progress": status_counts["in_progress"],
            "cancelled": status_counts["cancelled"],
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": (
                round((status_counts["done"] / total) * 100, 2) if total > 0 else 0
            ),
        },
    }
