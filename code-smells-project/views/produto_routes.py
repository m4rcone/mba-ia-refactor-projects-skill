from flask import Blueprint, jsonify, request

from controllers import produto_controller

produto_bp = Blueprint("produtos", __name__)


@produto_bp.get("/produtos")
def listar():
    return jsonify({"dados": produto_controller.listar(), "sucesso": True}), 200


@produto_bp.get("/produtos/busca")
def buscar():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)

    resultados = produto_controller.pesquisar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@produto_bp.get("/produtos/<int:produto_id>")
def buscar_um(produto_id):
    return jsonify({"dados": produto_controller.buscar(produto_id), "sucesso": True}), 200


@produto_bp.post("/produtos")
def criar():
    novo_id = produto_controller.criar(request.get_json(silent=True))
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


@produto_bp.put("/produtos/<int:produto_id>")
def atualizar(produto_id):
    produto_controller.atualizar(produto_id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@produto_bp.delete("/produtos/<int:produto_id>")
def deletar(produto_id):
    produto_controller.deletar(produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
