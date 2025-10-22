import re


def is_empty(text: str | None) -> bool:
    """Kiểm tra xem chuỗi có rỗng không."""
    return not text or text.strip() == ""


def is_too_long(text: str, max_length: int = 60) -> bool:
    """Kiểm tra độ dài chuỗi vượt quá giới hạn."""
    return len(text.strip()) > max_length


def is_too_short(text: str, min_length: int = 2) -> bool:
    """Kiểm tra độ dài chuỗi quá ngắn."""
    return len(text.strip()) < min_length


def is_link(text: str) -> bool:
    """Kiểm tra xem chuỗi có chứa URL hoặc link."""
    return bool(re.search(r"https?://|www\.", text.strip(), re.IGNORECASE))


def is_code(text: str) -> bool:
    """
    Kiểm tra xem chuỗi có chứa mã code (JS, SQL, HTML...) không.
    Dùng để phát hiện input độc hại hoặc code injection.
    """
    trimmed = text.strip()

    # HTML / Script tags
    if re.search(r"[<>]", trimmed) or re.search(r"<script\b[^>]*>.*?</script>", trimmed, re.IGNORECASE):
        return True

    # JavaScript keywords
    js_pattern = r"\b(if|else|function|while|for|return|var|let|const|=>|true|false|null|undefined)\b"
    if re.search(js_pattern, trimmed):
        return True

    # Code characters
    if re.search(r"[{}();=\[\]]", trimmed):
        return True

    # SQL keywords
    sql_pattern = r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|FROM|WHERE|TABLE|VALUES)\b"
    return bool(re.search(sql_pattern, trimmed, re.IGNORECASE))


def is_numeric(text: str) -> bool:
    """Kiểm tra chuỗi chỉ chứa số."""
    return bool(re.fullmatch(r"\d+", text.strip()))


def is_email(text: str) -> bool:
    """Kiểm tra định dạng email."""
    return bool(re.fullmatch(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", text.strip()))
