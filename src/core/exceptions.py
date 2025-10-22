from typing import Any, Dict


class AppError(Exception):
    """Base exception cho toàn bộ app."""
    status_code: int = 500
    message: str = "Internal Server Error"
    errors: Dict[str, Any] | None = None

    def __init__(self, message: str | None = None, errors: Dict[str, Any] | None = None):
        if message:
            self.message = message
        if errors:
            self.errors = errors
        super().__init__(self.message)


class ValidationError(AppError):
    status_code = 400
    message: str = "Invalid Request"


class ConflictError(AppError):
    status_code = 409
    message: str = "Conflict"


class DoNotPermissionError(AppError):
    status_code = 403
    message = "Forbidden"
    error = "Bạn không có quyền hạn cho thao tác này."

    def __init__(self):
        super().__init__(errors={"message": self.error})

class UnauthorizedError(AppError):
    status_code = 401
    message = "Unauthorized"
    error = "Bạn cần đăng nhập để thực hiện thao tác này."

    def __init__(self):
        super().__init__(errors={"message": self.error})


class ServerError(AppError):
    """Lỗi hệ thống - database, external service,..."""
    status_code = 500
    message = "Internal Server Error"

    def __init__(self, detail: str | None = None, errors: dict | None = None):
        super().__init__(
            message=self.message,
            errors=errors or {"message": detail or "Hệ thống đã xảy ra lỗi, Vui lòng thử lại sau."},
        )
