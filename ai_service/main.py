"""
SafeFlow AI - FastAPI application for scam risk analysis.

This is a standalone service that provides a REST API for analyzing text
for scam and fraud risk using OpenAI's GPT model.

Endpoint:
  POST /analyze

Input:
  {
    "text": string
  }

Output:
  {
    "riskScore": integer,
    "riskLevel": "low" | "medium" | "high",
    "detectedScamType": string | null,
    "explanation": string,
    "indicators": string[],
    "evidence": [
      {
        "text": string,
        "reason": string,
        "severity": "low" | "medium" | "high"
      }
    ],
    "recommendation": string
  }
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI

from .schemas import ScamAnalysisRequest, ScamAnalysisResponse
from .analyzer import ScamAiAnalyzer
from .main_service import ScamAnalysisService
from .errors import ScamAnalysisError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

SERVICE_DIR = Path(__file__).resolve().parent
SERVICE_ENV_PATH = SERVICE_DIR / ".env"


# Global instances
_analyzer: ScamAiAnalyzer | None = None
_service: ScamAnalysisService | None = None


def load_service_environment() -> None:
    """Load ai_service configuration from a local .env file when present."""
    if SERVICE_ENV_PATH.exists():
        load_dotenv(SERVICE_ENV_PATH, override=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    Initializes OpenAI client and analyzer on startup,
    cleans up on shutdown.
    """
    global _analyzer, _service
    
    # Startup
    logger.info("Starting SafeFlow AI service")
    load_service_environment()
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable not set. Define it in the shell or in ai_service/.env."
        )
    
    openai_client = OpenAI(api_key=openai_api_key)
    _analyzer = ScamAiAnalyzer(openai_client)
    _service = ScamAnalysisService(_analyzer)
    
    logger.info("SafeFlow AI service initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SafeFlow AI service")


# Create FastAPI app
app = FastAPI(
    title="SafeFlow AI",
    description="Scam risk analysis service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/analyze", response_model=ScamAnalysisResponse)
async def analyze(request: ScamAnalysisRequest) -> ScamAnalysisResponse:
    """
    Analyze text for scam and fraud risk.
    
    Args:
        request: ScamAnalysisRequest with 'text' field
    
    Returns:
        ScamAnalysisResponse with risk analysis
    
    Raises:
        HTTPException: With error code and details if analysis fails
    """
    if _service is None:
        raise HTTPException(
            status_code=503,
            detail={
                "errorCode": "SERVICE_UNAVAILABLE",
                "message": "Service not initialized",
            },
        )
    
    try:
        response = await _service.analyze_text(request.text)
        return response
    except ScamAnalysisError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.to_api_error_dict(),
        )
    except Exception as err:
        logger.error(f"Unexpected error in /analyze endpoint", exc_info=err)
        raise HTTPException(
            status_code=500,
            detail={
                "errorCode": "SERVER_ERROR",
                "message": "An unexpected error occurred",
            },
        )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        {"status": "ok"}
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
    )
