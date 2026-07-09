from models import pedido_model

_FAIXAS_DESCONTO = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]


def _calcular_desconto(faturamento):
    for limite, percentual in _FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * percentual
    return 0


def vendas():
    resumo = pedido_model.get_sales_summary()
    total_pedidos = resumo["total_pedidos"]
    faturamento = resumo["faturamento"]
    por_status = resumo["por_status"]

    desconto = _calcular_desconto(faturamento)
    ticket_medio = faturamento / total_pedidos if total_pedidos > 0 else 0

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": por_status.get("pendente", 0),
        "pedidos_aprovados": por_status.get("aprovado", 0),
        "pedidos_cancelados": por_status.get("cancelado", 0),
        "ticket_medio": round(ticket_medio, 2),
    }
