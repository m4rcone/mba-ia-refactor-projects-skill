from werkzeug.security import check_password_hash, generate_password_hash

from models import usuario_model
from middlewares.errors import NotFoundError, UnauthorizedError, ValidationError


def listar():
    return usuario_model.get_all()


def buscar(usuario_id):
    usuario = usuario_model.get_by_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return usuario


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")

    return usuario_model.create(nome, email, generate_password_hash(senha))


def login(dados):
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    usuario = usuario_model.get_by_email(email)
    if not usuario or not check_password_hash(usuario["senha"], senha):
        raise UnauthorizedError("Email ou senha inválidos", payload={"sucesso": False})

    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "tipo": usuario["tipo"],
    }
