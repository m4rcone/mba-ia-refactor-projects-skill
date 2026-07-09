import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    status = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    status = 400


class UnauthorizedError(AppError):
    status = 401


class ForbiddenError(AppError):
    status = 403


class NotFoundError(AppError):
    status = 404


class ConflictError(AppError):
    status = 409


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return {"error": error.message}, error.status

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception(error)
        return {"error": "Erro interno"}, 500
