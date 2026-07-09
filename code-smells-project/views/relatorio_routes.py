from flask import Blueprint, jsonify

from controllers import relatorio_controller

relatorio_bp = Blueprint("relatorios", __name__)


@relatorio_bp.get("/relatorios/vendas")
def vendas():
    return jsonify({"dados": relatorio_controller.vendas(), "sucesso": True}), 200
