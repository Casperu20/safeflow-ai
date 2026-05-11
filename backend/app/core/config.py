from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "safeflow-ai-backend"
    environment: str = os.getenv("ENVIRONMENT", "development")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    ai_service_url: str = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000")


settings = Settings()