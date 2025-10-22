import re

def is_safe_input(text: str) -> bool:
    """
    Kiểm tra input có chứa các mẫu tấn công XSS hoặc SQL injection không.
    """
    if not text:
        return True

    patterns = [
        r"<script\b[^>]*>",  # XSS
        r"onerror\s*=",
        r"onload\s*=",
        r"(SELECT|INSERT|DELETE|UPDATE|DROP|UNION|FROM|WHERE)\b",  # SQL
        r"--",  # SQL comment
        r";",  # SQL statement separator
    ]

    return not any(re.search(p, text, re.IGNORECASE) for p in patterns)
