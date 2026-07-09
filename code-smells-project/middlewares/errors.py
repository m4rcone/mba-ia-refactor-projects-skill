class AppError(Exception):
    status = 500

    def __init__(self, message, status=None, payload=None):
        super().__init__(message)
        self.message = message
        if status is not None:
            self.status = status
        self.payload = payload or {}

    def to_body(self):
        body = {"erro": self.message}
        body.update(self.payload)
        return body


class ValidationError(AppError):
    status = 400


class NotFoundError(AppError):
    status = 404


class UnauthorizedError(AppError):
    status = 401
