from constants import DEFAULT_COLOR
from middlewares.error_handler import NotFoundError, ValidationError
from models.category import Category
from models.task import Task


def list_categories():
    result = []
    for category in Category.get_all():
        data = category.to_dict()
        data["task_count"] = Task.count_by_category(category.id)
        result.append(data)
    return result


def create_category(data):
    if not data:
        raise ValidationError("Dados inválidos")

    name = data.get("name")
    if not name:
        raise ValidationError("Nome é obrigatório")

    category = Category()
    category.name = name
    category.description = data.get("description", "")
    category.color = data.get("color", DEFAULT_COLOR)

    category.save()
    return category.to_dict()


def update_category(category_id, data):
    category = _get_or_404(category_id)
    data = data or {}

    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    if "color" in data:
        category.color = data["color"]

    category.save()
    return category.to_dict()


def delete_category(category_id):
    category = _get_or_404(category_id)
    category.delete()
    return {"message": "Categoria deletada"}


def _get_or_404(category_id):
    category = Category.get_by_id(category_id)
    if not category:
        raise NotFoundError("Categoria não encontrada")
    return category
