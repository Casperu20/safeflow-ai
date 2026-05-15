import re


CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
INLINE_WHITESPACE_RE = re.compile(r"[^\S\n]+")
MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
URL_RE = re.compile(r"\b(?:https?://|www\.)\S+\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:(?<!\w)\+?\d(?:[\s().-]*\d){8,}(?!\w))")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.IGNORECASE)
LONG_DIGIT_SEQUENCE_RE = re.compile(r"\b(?:\d[ -]?){8,}\d\b")


def sanitize_text_content(content: str) -> str:
    return normalize_extracted_text(content)


def normalize_extracted_text(content: str) -> str:
    if not content:
        return ""

    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    normalized = CONTROL_CHAR_RE.sub("", normalized)

    lines = []
    for line in normalized.split("\n"):
        cleaned_line = INLINE_WHITESPACE_RE.sub(" ", line).strip()
        lines.append(cleaned_line)

    normalized = "\n".join(lines)
    normalized = MULTI_NEWLINE_RE.sub("\n\n", normalized)
    return normalized.strip()


def redact_sensitive_text(content: str) -> str:
    redacted = normalize_extracted_text(content)
    redacted = EMAIL_RE.sub("[redacted-email]", redacted)
    redacted = URL_RE.sub("[redacted-url]", redacted)
    redacted = IBAN_RE.sub("[redacted-iban]", redacted)
    redacted = PHONE_RE.sub("[redacted-phone]", redacted)
    redacted = LONG_DIGIT_SEQUENCE_RE.sub("[redacted-number]", redacted)
    return redacted


def safe_text_excerpt(content: str, max_length: int = 120) -> str:
    sanitized = redact_sensitive_text(content)

    if not sanitized:
        return "[redacted]"

    if len(sanitized) <= max_length:
        return sanitized

    return f"{sanitized[: max_length - 3].rstrip()}..."