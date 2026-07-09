import logging
import re

from constants import EMAIL_REGEX, MIN_PASSWORD_LENGTH, VALID_USER_ROLES
from middlewares.error_handler import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from models.task import Task
from models.user import User

logger = logging.getLogger(__name__)


def list_users():
    return [user.to_dict_with_task_count() for user in User.get_all()]


def get_user(user_id):
    user = _get_or_404(user_id)
    data = user.to_dict()
    data["tasks"] = [task.to_dict() for task in Task.get_by_user(user_id)]
    return data


def create_user(data):
    if not data:
        raise ValidationError("Dados inválidos")

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        raise ValidationError("Nome é obrigatório")
    if not email:
        raise ValidationError("Email é obrigatório")
    if not password:
        raise ValidationError("Senha é obrigatória")

    _validate_email(email)
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError("Senha deve ter no mínimo 4 caracteres")
    if User.get_by_email(email):
        raise ConflictError("Email já cadastrado")
    _validate_role(role)

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    user.save()
    logger.info("Usuário criado: %s - %s", user.id, user.name)
    return user.to_dict()


def update_user(user_id, data):
    user = _get_or_404(user_id)
    if not data:
        raise ValidationError("Dados inválidos")

    if "name" in data:
        user.name = data["name"]

    if "email" in data:
        _validate_email(data["email"])
        existing = User.get_by_email(data["email"])
        if existing and existing.id != user_id:
            raise ConflictError("Email já cadastrado")
        user.email = data["email"]

    if "password" in data:
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            raise ValidationError("Senha muito curta")
        user.set_password(data["password"])

    if "role" in data:
        _validate_role(data["role"])
        user.role = data["role"]

    if "active" in data:
        user.active = data["active"]

    user.save()
    return user.to_dict()


def delete_user(user_id):
    user = _get_or_404(user_id)
    user.delete_with_tasks()
    logger.info("Usuário deletado: %s", user_id)
    return {"message": "Usuário deletado com sucesso"}


def get_user_tasks(user_id):
    _get_or_404(user_id)
    return [task.to_summary() for task in Task.get_by_user(user_id)]


def login(data):
    if not data:
        raise ValidationError("Dados inválidos")

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise ValidationError("Email e senha são obrigatórios")

    user = User.get_by_email(email)
    if not user or not user.check_password(password):
        raise UnauthorizedError("Credenciais inválidas")
    if not user.active:
        raise ForbiddenError("Usuário inativo")

    return {
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": "fake-jwt-token-" + str(user.id),
    }


def _get_or_404(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    return user


def _validate_email(email):
    if not re.match(EMAIL_REGEX, email):
        raise ValidationError("Email inválido")


def _validate_role(role):
    if role not in VALID_USER_ROLES:
        raise ValidationError("Role inválido")
