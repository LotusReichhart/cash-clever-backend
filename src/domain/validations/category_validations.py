from src.core.utils.validations.base_validation import is_empty, is_too_short
from src.core.utils.validations.security_validation import is_safe_input


def validate_name(name: str) -> str | None:
    name = name.strip()
    if is_empty(name):
        return "Vui lòng nhập tên danh mục"
    if is_too_short(name, 2):
        return "Tên danh mục phải có ít nhất 2 ký tự"
    if not is_safe_input(name):
        return "Tên danh mục chứa ký tự không an toàn"
    return None
