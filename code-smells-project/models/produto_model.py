from database import db_cursor


def _to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM produtos")
        return [_to_dict(row) for row in cursor.fetchall()]


def get_by_id(produto_id):
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return _to_dict(row) if row else None


def create(nome, descricao, preco, estoque, categoria):
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        return cursor.lastrowid


def update(produto_id, nome, descricao, preco, estoque, categoria):
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )


def delete(produto_id):
    with db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))


def search(termo, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like = "%" + termo + "%"
        params.extend([like, like])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    with db_cursor() as cursor:
        cursor.execute(query, params)
        return [_to_dict(row) for row in cursor.fetchall()]
