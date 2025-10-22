from src.core.exceptions import AppError


class EmailAlreadyUsedError(AppError):
    status_code = 409
    message = "Conflict"
    error = "Email này đã đăng ký tài khoản."

    def __init__(self):
        super().__init__(errors={"email": self.error})


class EmailNotRegisteredError(AppError):
    status_code = 404
    message = "Not Found"
    error = "Email này chưa đăng ký tài khoản."

    def __init__(self):
        super().__init__(errors={"email": self.error})


class OTPIncorrectError(AppError):
    status_code = 400
    message = "Invalid Request"
    error = "OTP không khớp."

    def __init__(self):
        super().__init__(errors={"otp": self.error})


class TooManyOtpRequestsError(AppError):
    status_code = 429
    message = "To Many Requests"
    error = "Yêu cầu OTP quá nhiều lần, vui lòng thử lại sau."

    def __init__(self):
        super().__init__(errors={"message": self.error})


class TokenExpiredError(AppError):
    status_code = 401
    message = "Token expired"
    error = "Mã xác thực đã hết hạn, vui lòng yêu cầu mã mới."

    def __init__(self):
        super().__init__(errors={"token": self.error})


class TokenInvalidError(AppError):
    status_code = 401
    message = "Invalid token"
    error = "Mã xác thực không hợp lệ."

    def __init__(self):
        super().__init__(errors={"token": self.error})


class IncorrectPasswordError(AppError):
    status_code = 409
    message = "Conflict"
    error = "Mật khẩu không đúng."

    def __init__(self):
        super().__init__(errors={"password": self.error})

class UserNotFoundError(AppError):
    status_code = 404
    message = "Not Found"
    error = "Người dùng không tồn tại."

    def __init__(self):
        super().__init__(errors={"user": self.error})
