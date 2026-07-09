import logging

from models import pedido_model, produto_model
from middlewares.errors import ValidationError

logger = logging.getLogger(__name__)

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def listar():
    return pedido_model.get_all()


def listar_por_usuario(usuario_id):
    return pedido_model.get_by_usuario(usuario_id)


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    total = 0
    itens_persistir = []
    for item in itens:
        produto = produto_model.get_by_id(item["produto_id"])
        if produto is None:
            raise ValidationError(
                "Produto " + str(item["produto_id"]) + " não encontrado",
                payload={"sucesso": False},
            )
        if produto["estoque"] < item["quantidade"]:
            raise ValidationError(
                "Estoque insuficiente para " + produto["nome"], payload={"sucesso": False}
            )
        total += produto["preco"] * item["quantidade"]
        itens_persistir.append(
            {
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"],
            }
        )

    pedido_id = pedido_model.create(usuario_id, itens_persistir, total)
    _notificar_criacao(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, dados):
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_VALIDOS:
        raise ValidationError("Status inválido")

    pedido_model.update_status(pedido_id, novo_status)
    _notificar_status(pedido_id, novo_status)


def _notificar_criacao(pedido_id, usuario_id):
    logger.info("Pedido %s criado para usuário %s", pedido_id, usuario_id)
    logger.info("Notificações (email/sms/push) disparadas para o pedido %s", pedido_id)


def _notificar_status(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("Pedido %s aprovado — preparar envio", pedido_id)
    elif novo_status == "cancelado":
        logger.info("Pedido %s cancelado — devolver estoque", pedido_id)
