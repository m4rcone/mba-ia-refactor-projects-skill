from database import db_cursor


def _to_public_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios")
        return [_to_public_dict(row) for row in cursor.fetchall()]


def get_by_id(usuario_id):
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return _to_public_dict(row) if row else None


def get_by_email(email):
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cursor.fetchone()


def create(nome, email, senha_hash, tipo="cliente"):
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
        return cursor.lastrowid
