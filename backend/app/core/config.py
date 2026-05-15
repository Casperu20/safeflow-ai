from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env", override=False)


def _get_env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass
class Settings:
    app_name: str = "safeflow-ai-backend"
    environment: str = os.getenv("ENVIRONMENT", "development")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5173")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./safeflow.db")
    ai_service_url: str = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8001")
    ai_service_timeout_seconds: float = _get_env_float("AI_SERVICE_TIMEOUT_SECONDS", 60.0)
    analysis_mode: str = (os.getenv("ANALYSIS_MODE", "ai").strip().lower() or "ai")
    jwt_secret_key: str | None = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = _get_env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)
    ocr_enabled: bool = _get_env_bool("OCR_ENABLED", True)
    ocr_lang: str = os.getenv("OCR_LANG", "eng").strip() or "eng"
    ocr_timeout_seconds: float = _get_env_float("OCR_TIMEOUT_SECONDS", 20.0)
    max_file_size_mb: int = _get_env_int("MAX_FILE_SIZE_MB", 10)
    max_pdf_pages: int = _get_env_int("MAX_PDF_PAGES", 5)
    max_image_width: int = _get_env_int("MAX_IMAGE_WIDTH", 4000)
    max_image_height: int = _get_env_int("MAX_IMAGE_HEIGHT", 4000)
    min_extracted_text_chars: int = _get_env_int("MIN_EXTRACTED_TEXT_CHARS", 20)
    max_text_length: int = _get_env_int("MAX_TEXT_LENGTH", 10_000)
    max_ai_input_chars: int = _get_env_int("MAX_AI_INPUT_CHARS", 20_000)

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"


settings = Settings()