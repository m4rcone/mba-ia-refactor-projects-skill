from models import produto_model
from middlewares.errors import NotFoundError, ValidationError

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
NOME_MIN = 2
NOME_MAX = 200


def listar():
    return produto_model.get_all()


def buscar(produto_id):
    produto = produto_model.get_by_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado", payload={"sucesso": False})
    return produto


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    _exigir_campos(dados)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    _validar_valores(preco, estoque)
    if len(nome) < NOME_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return produto_model.create(nome, descricao, preco, estoque, categoria)


def atualizar(produto_id, dados):
    if not produto_model.get_by_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    if not dados:
        raise ValidationError("Dados inválidos")
    _exigir_campos(dados)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    _validar_valores(preco, estoque)
    produto_model.update(produto_id, nome, descricao, preco, estoque, categoria)


def deletar(produto_id):
    if not produto_model.get_by_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    produto_model.delete(produto_id)


def pesquisar(termo, categoria, preco_min, preco_max):
    return produto_model.search(termo, categoria, preco_min, preco_max)


def _exigir_campos(dados):
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")


def _validar_valores(preco, estoque):
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
