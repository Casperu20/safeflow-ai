import re


WHITESPACE_RE = re.compile(r"\s+")
LONG_DIGIT_SEQUENCE_RE = re.compile(r"\b\d{4,}\b")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def sanitize_text_content(content: str) -> str:
    return WHITESPACE_RE.sub(" ", content).strip()


def safe_text_excerpt(content: str, max_length: int = 80) -> str:
    sanitized = sanitize_text_content(content)
    sanitized = EMAIL_RE.sub("[redacted-email]", sanitized)
    sanitized = LONG_DIGIT_SEQUENCE_RE.sub("[redacted-number]", sanitized)

    if not sanitized:
        return "[redacted]"

    if len(sanitized) <= max_length:
        return sanitized

    return f"{sanitized[: max_length - 3].rstrip()}..."