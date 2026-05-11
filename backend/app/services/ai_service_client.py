import httpx

from app.core.config import settings
from app.schemas.errors import ApiError
from app.schemas.scam_analysis import AiServiceResponse


class AiServiceClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: float = 10.0) -> None:
        self.base_url = (base_url or settings.ai_service_url).rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def analyze_text(self, text: str) -> AiServiceResponse:
        url = f"{self.base_url}/analyze"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, json={"text": text})
        except httpx.TimeoutException as exc:
            raise ApiError(
                status_code=504,
                error_code="AI_SERVICE_TIMEOUT",
                message="AI service request timed out.",
                details={"serviceUrl": self.base_url},
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