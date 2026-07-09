from flask import Blueprint, jsonify, request

from controllers import usuario_controller

usuario_bp = Blueprint("usuarios", __name__)


@usuario_bp.get("/usuarios")
def listar():
    return jsonify({"dados": usuario_controller.listar(), "sucesso": True}), 200


@usuario_bp.get("/usuarios/<int:usuario_id>")
def buscar(usuario_id):
    return jsonify({"dados": usuario_controller.buscar(usuario_id), "sucesso": True}), 200


@usuario_bp.post("/usuarios")
def criar():
    novo_id = usuario_controller.criar(request.get_json(silent=True))
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


@usuario_bp.post("/login")
def login():
    usuario = usuario_controller.login(request.get_json(silent=True) or {})
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
