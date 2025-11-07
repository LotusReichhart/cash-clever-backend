from src.domain.exceptions.app_exceptions import (
    ConflictError,
    NotFoundError,
    BadRequestError,
    TooManyRequestsError
)


class EmailAlreadyUsedError(ConflictError):
    error = "Email này đã đăng ký tài khoản."

    def __init__(self):
        super().__init__(errors={"email": self.error})


class EmailNotRegisteredError(NotFoundError):
    error = "Email này chưa đăng ký tài khoản."

    def __init__(self):
        super().__init__(errors={"email": self.error})


class OtpIncorrectError(BadRequestError):
    error = "OTP không khớp."

    def __init__(self):
        super().__init__(errors={"otp": self.error})


class TooManyOtpRequestsError(TooManyRequestsError):
    error = "Yêu cầu OTP quá nhiều lần, vui lòng thử lại sau."

    def __init__(self):
        super().__init__(errors={"message": self.error})


class IncorrectPasswordError(ConflictError):
    error = "Mật khẩu không đúng."

    def __init__(self):
        super().__init__(errors={"password": self.error})


class UserNotFoundError(NotFoundError):
    error = "Người dùng không tồn tại."

    def __init__(self):
        super().__init__(errors={"user": self.error})
