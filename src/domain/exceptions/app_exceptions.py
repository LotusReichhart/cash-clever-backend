from typing import Any, Dict


class AppError(Exception):
    """Base exception cho toàn bộ di."""
    status_code: int = 503
    message: str = "Service Unavailable"
    errors: Dict[str, Any] | None = None

    def __init__(self, message: str | None = None, errors: Dict[str, Any] | None = None):
        if message:
            self.message = message
        if errors:
            self.errors = errors
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = 400
    message: str = "Bad Request"


class UnauthorizedError(AppError):
    status_code = 401
    message = "Unauthorized"
    error = "Bạn cần đăng nhập để thực hiện thao tác này."

    def __init__(self):
        super().__init__(errors={"message": self.error})


class ForbiddenError(AppError):
    status_code = 403
    message = "Forbidden"
    error = "Bạn không có quyền hạn cho thao tác này."

    def __init__(self):
        super().__init__(errors={"message": self.error})


class NotFoundError(AppError):
    status_code = 404
    message = "Not Found"


class ConflictError(AppError):
    status_code = 409
    message: str = "Conflict"


class TooManyRequestsError(AppError):
    status_code = 429
    message: str = "Too Many Requests"
    errors = "Bạn đang thao tác quá nhanh. Vui lòng thử lại sau ít phút."


class ServerError(AppError):
    """Lỗi hệ thống - database, external service,..."""
    status_code = 500
    message = "Internal Server Error"

    def __init__(self, detail: str | None = None, errors: dict | None = None):
        super().__init__(
            message=self.message,
            errors=errors or {"message": detail or "Hệ thống đã xảy ra lỗi, Vui lòng thử lại sau."},
        )
