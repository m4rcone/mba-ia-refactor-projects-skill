import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Config
from database import init_db
from middlewares.error_handler import register_error_handlers
from views.pedido_routes import pedido_bp
from views.produto_routes import produto_bp
from views.relatorio_routes import relatorio_bp
from views.system_routes import system_bp
from views.usuario_routes import usuario_bp


def create_app():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    with app.app_context():
        init_db()

    for blueprint in (produto_bp, usuario_bp, pedido_bp, relatorio_bp, system_bp):
        app.register_blueprint(blueprint)

    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
