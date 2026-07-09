import logging
from datetime import datetime

from constants import (
    DEFAULT_PRIORITY,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_TASK_STATUSES,
)
from middlewares.error_handler import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from utils.dates import utcnow

logger = logging.getLogger(__name__)


def list_tasks():
    return [task.to_dict_enriched() for task in Task.get_all_with_relations()]


def get_task(task_id):
    task = _get_or_404(task_id)
    return task.to_dict_detailed()


def create_task(data):
    if not data:
        raise ValidationError("Dados inválidos")

    title = data.get("title")
    if not title:
        raise ValidationError("Título é obrigatório")
    _validate_title_length(title)

    status = data.get("status", "pending")
    priority = data.get("priority", DEFAULT_PRIORITY)
    _validate_status(status)
    _validate_priority(priority)

    user_id = data.get("user_id")
    category_id = data.get("category_id")
    _ensure_user_exists(user_id)
    _ensure_category_exists(category_id)

    task = Task()
    task.title = title
    task.description = data.get("description", "")
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get("due_date")
    if due_date:
        task.due_date = _parse_due_date(
            due_date, "Formato de data inválido. Use YYYY-MM-DD"
        )

    task.tags = _normalize_tags(data.get("tags"))

    task.save()
    logger.info("Task criada: %s - %s", task.id, task.title)
    return task.to_dict()


def update_task(task_id, data):
    task = _get_or_404(task_id)
    if not data:
        raise ValidationError("Dados inválidos")

    if "title" in data:
        _validate_title_length(data["title"])
        task.title = data["title"]

    if "description" in data:
        task.description = data["description"]

    if "status" in data:
        _validate_status(data["status"])
        task.status = data["status"]

    if "priority" in data:
        _validate_priority(data["priority"])
        task.priority = data["priority"]

    if "user_id" in data:
        _ensure_user_exists(data["user_id"])
        task.user_id = data["user_id"]

    if "category_id" in data:
        _ensure_category_exists(data["category_id"])
        task.category_id = data["category_id"]

    if "due_date" in data:
        task.due_date = (
            _parse_due_date(data["due_date"], "Formato de data inválido")
            if data["due_date"]
            else None
        )

    if "tags" in data:
        task.tags = _normalize_tags(data["tags"])

    task.updated_at = utcnow()
    task.save()
    logger.info("Task atualizada: %s", task.id)
    return task.to_dict()


def delete_task(task_id):
    task = _get_or_404(task_id)
    task.delete()
    logger.info("Task deletada: %s", task_id)
    return {"message": "Task deletada com sucesso"}


def search_tasks(text, status, priority, user_id):
    return [
        task.to_dict()
        for task in Task.search(
            text=text or None,
            status=status or None,
            priority=_to_int(priority, "Prioridade inválida") if priority else None,
            user_id=_to_int(user_id, "user_id inválido") if user_id else None,
        )
    ]


def get_stats():
    total = Task.count()
    done = Task.count_by_status("done")
    overdue = sum(1 for task in Task.get_all() if task.is_overdue())
    return {
        "total": total,
        "pending": Task.count_by_status("pending"),
        "in_progress": Task.count_by_status("in_progress"),
        "done": done,
        "cancelled": Task.count_by_status("cancelled"),
        "overdue": overdue,
        "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
    }


def _get_or_404(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        raise NotFoundError("Task não encontrada")
    return task


def _validate_title_length(title):
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")


def _validate_status(status):
    if status not in VALID_TASK_STATUSES:
        raise ValidationError("Status inválido")


def _validate_priority(priority):
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValidationError("Prioridade deve ser entre 1 e 5")


def _ensure_user_exists(user_id):
    if user_id and not User.get_by_id(user_id):
        raise NotFoundError("Usuário não encontrado")


def _ensure_category_exists(category_id):
    if category_id and not Category.get_by_id(category_id):
        raise NotFoundError("Categoria não encontrada")


def _parse_due_date(value, message):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValidationError(message)


def _normalize_tags(tags):
    if not tags:
        return None
    return ",".join(tags) if isinstance(tags, list) else tags


def _to_int(value, message):
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValidationError(message)
