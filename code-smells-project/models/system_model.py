from database import db_cursor

_RESET_TABLES = ["itens_pedido", "pedidos", "produtos", "usuarios"]


def health_counts():
    with db_cursor() as cursor:
        cursor.execute("SELECT 1")
        counts = {}
        for tabela in ("produtos", "usuarios", "pedidos"):
            cursor.execute("SELECT COUNT(*) FROM " + tabela)
            counts[tabela] = cursor.fetchone()[0]
    return counts


def reset():
    with db_cursor(commit=True) as cursor:
        for tabela in _RESET_TABLES:
            cursor.execute("DELETE FROM " + tabela)


def run_query(sql):
    with db_cursor() as cursor:
        cursor.execute(sql)
        if sql.strip().upper().startswith("SELECT"):
            return {"dados": [dict(row) for row in cursor.fetchall()], "sucesso": True}
        cursor.connection.commit()
        return {"mensagem": "Query executada", "sucesso": True}
