import re

from src.core.utils.validations.base_validation import is_empty, is_too_short, is_email
from src.core.utils.validations.security_validation import is_safe_input


def validate_name(name: str) -> str | None:
    name = name.strip()
    if is_empty(name):
        return "Vui lòng nhập tên của bạn"
    if is_too_short(name, 2):
        return "Tên phải có ít nhất 2 ký tự"
    if not is_safe_input(name):
        return "Tên chứa ký tự không an toàn"
    return None


def validate_email(email: str) -> str | None:
    email = email.strip()
    if is_empty(email):
        return "Vui lòng nhập email của bạn"
    if not is_email(email):
        return "Email không hợp lệ"
    if not is_safe_input(email):
        return "Email chứa ký tự không an toàn"
    return None


def validate_password(password: str) -> str | None:
    password = password.strip()

    if is_empty(password):
        return "Vui lòng nhập mật khẩu của bạn"
    if is_too_short(password, 8):
        return "Mật khẩu phải có ít nhất 8 ký tự"
    if not re.search(r"[A-Z]", password):
        return "Mật khẩu phải chứa ít nhất 1 chữ cái in hoa"
    if not re.search(r"[a-z]", password):
        return "Mật khẩu phải chứa ít nhất 1 chữ cái thường"
    if not re.search(r"[0-9]", password):
        return "Mật khẩu phải chứa ít nhất 1 chữ số"
    if not re.search(r"[\W_]", password):
        return "Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt"
    if not is_safe_input(password):
        return "Mật khẩu chứa ký tự không an toàn"

    return None


def validate_otp(otp: str) -> str | None:
    otp = otp.strip()

    if is_empty(otp):
        return "Vui lòng nhập mã OTP"

    return None
