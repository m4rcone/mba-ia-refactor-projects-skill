from database import db_cursor


def _fetch(where_clause="", params=()):
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM pedidos " + where_clause + " ORDER BY id", params)
        pedidos_rows = cursor.fetchall()
        if not pedidos_rows:
            return []

        pedido_ids = [row["id"] for row in pedidos_rows]
        placeholders = ",".join("?" for _ in pedido_ids)
        cursor.execute(
            "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, "
            "p.nome AS produto_nome "
            "FROM itens_pedido ip LEFT JOIN produtos p ON p.id = ip.produto_id "
            "WHERE ip.pedido_id IN (" + placeholders + ") ORDER BY ip.id",
            pedido_ids,
        )
        itens_por_pedido = {}
        for item in cursor.fetchall():
            itens_por_pedido.setdefault(item["pedido_id"], []).append(
                {
                    "produto_id": item["produto_id"],
                    "produto_nome": item["produto_nome"] or "Desconhecido",
                    "quantidade": item["quantidade"],
                    "preco_unitario": item["preco_unitario"],
                }
            )

    return [
        {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": itens_por_pedido.get(row["id"], []),
        }
        for row in pedidos_rows
    ]


def get_all():
    return _fetch()


def get_by_usuario(usuario_id):
    return _fetch("WHERE usuario_id = ?", (usuario_id,))


def create(usuario_id, itens, total):
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid
        for item in itens:
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        return pedido_id


def update_status(pedido_id, novo_status):
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id)
        )


def get_sales_summary():
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS total_pedidos, COALESCE(SUM(total), 0) AS faturamento FROM pedidos"
        )
        agg = cursor.fetchone()
        cursor.execute("SELECT status, COUNT(*) AS quantidade FROM pedidos GROUP BY status")
        por_status = {row["status"]: row["quantidade"] for row in cursor.fetchall()}
    return {
        "total_pedidos": agg["total_pedidos"],
        "faturamento": agg["faturamento"],
        "por_status": por_status,
    }
