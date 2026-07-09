from flask import Blueprint, jsonify, request

from config.settings import Config
from controllers import system_controller

system_bp = Blueprint("system", __name__)


@system_bp.get("/")
def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": Config.APP_VERSION,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


@system_bp.get("/health")
def health():
    return jsonify(system_controller.health()), 200


@system_bp.post("/admin/reset-db")
def reset_database():
    return jsonify(system_controller.reset_database()), 200


@system_bp.post("/admin/query")
def executar_query():
    return jsonify(system_controller.run_query(request.get_json(silent=True))), 200
