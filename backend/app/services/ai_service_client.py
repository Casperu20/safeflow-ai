import httpx

from app.core.config import settings
from app.schemas.errors import ApiError
from app.schemas.scam_analysis import AiServiceResponse


DEFAULT_CONNECT_TIMEOUT_SECONDS = 5.0


class AiServiceClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: float | None = None) -> None:
        self.base_url = (base_url or settings.ai_service_url).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.ai_service_timeout_seconds
        self.timeout = httpx.Timeout(
            self.timeout_seconds,
            connect=DEFAULT_CONNECT_TIMEOUT_SECONDS,
        )

    async def analyze_text(self, text: str) -> AiServiceResponse:
        url = f"{self.base_url}/analyze"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json={"text": text})
        except httpx.TimeoutException as exc:
            raise ApiError(
                status_code=504,
                error_code="AI_SERVICE_TIMEOUT",
                message="AI service request timed out.",
                details={
                    "serviceUrl": self.base_url,
                    "timeoutSeconds": self.timeout_seconds,
                },
            ) from exc
        except httpx.RequestError as exc:
            raise ApiError(
                status_code=503,
                error_code="AI_SERVICE_UNAVAILABLE",
                message="AI service is unavailable.",
                details={"serviceUrl": self.base_url},
            ) from exc

        if response.status_code >= 400:
            raise ApiError(
                status_code=502,
                error_code="AI_SERVICE_ERROR",
                message="AI service returned an error response.",
                details={
                    "statusCode": response.status_code,
                    "serviceUrl": self.base_url,
                },
            )

        try:
            payload = response.json()
            return AiServiceResponse.model_validate(payload)
        except Exception as exc:
            raise ApiError(
                status_code=502,
                error_code="AI_SERVICE_BAD_RESPONSE",
                message="AI service returned an invalid response.",
                details={"serviceUrl": self.base_url},
            ) from exc