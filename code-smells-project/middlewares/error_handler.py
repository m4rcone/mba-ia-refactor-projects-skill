import logging

from flask import jsonify

from middlewares.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify(error.to_body()), error.status

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Erro não tratado", exc_info=error)
        return jsonify({"erro": "Erro interno do servidor"}), 500
