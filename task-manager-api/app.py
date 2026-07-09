import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Config
from database import db
from middlewares.error_handler import register_error_handlers
from utils.dates import utcnow
from views.category_routes import category_bp
from views.report_routes import report_bp
from views.task_routes import task_bp
from views.user_routes import user_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    logging.basicConfig(level=logging.INFO)
    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(report_bp)
    register_error_handlers(app)

    @app.route("/health")
    def health():
        return {"status": "ok", "timestamp": str(utcnow())}

    @app.route("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host=app.config["HOST"], port=app.config["PORT"])
