from json import JSONDecodeError
from uuid import uuid4
import logging

from fastapi import APIRouter, Request
from starlette.datastructures import UploadFile

from app.schemas.errors import ApiError, ErrorResponse
from app.schemas.scam_analysis import AiServiceResponse, ScamAnalysisConfigResponse, ScamAnalysisResponse
from app.services.ai_service_client import AiServiceClient
from app.services.scam_analysis_service import AnalysisSubmission, ScamAnalysisService
from app.utils.text_sanitization import sanitize_text_content

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/scam-analysis", tags=["scam-analysis"])
service = ScamAnalysisService()
ai_service_client = AiServiceClient()


@router.get(
    "/config",
    response_model=ScamAnalysisConfigResponse,
)
async def get_scam_analysis_config() -> ScamAnalysisConfigResponse:
    return service.get_config()


@router.post(
    "",
    response_model=ScamAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_scam_submission(request: Request) -> ScamAnalysisResponse:
    submission = await _parse_submission(request)

    try:
        if submission.input_type == "text":
            if submission.file is not None:
                raise ApiError(
                    status_code=400,
                    error_code="INVALID_REQUEST",
                    message="Text analysis accepts content only.",
                    details={
                        "file": ["Do not upload a file when inputType is text."],
                    },
                )

            content = sanitize_text_content(submission.content or "")
            if not content:
                raise ApiError(
                    status_code=400,
                    error_code="EMPTY_TEXT_CONTENT",
                    message="Text content cannot be empty.",
                    details={
                        "content": ["This field is required when inputType is text."],
                    },
                )

            ai_response = AiServiceResponse.model_validate(
                await ai_service_client.analyze_text(content)
            )
            logger.info(f"AI response received: {ai_response}")
            return ScamAnalysisResponse(
                analysisId=f"analysis_{uuid4()}",
                riskScore=ai_response.riskScore,
                riskLevel=ai_response.riskLevel,
                detectedScamType=ai_response.detectedScamType,
                explanation=ai_response.explanation,
                indicators=ai_response.indicators or [],
                recommendation=ai_response.recommendation,
                evidence=ai_response.evidence or [],
                analysisMode="ai",
            )

        return await service.analyze(submission)
    except ApiError:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during analysis")
        raise ApiError(
            status_code=500,
            error_code="ANALYSIS_FAILED",
            message="Analysis could not be completed.",
            details={},
        ) from exc


async def _parse_submission(request: Request) -> AnalysisSubmission:
    content_type = (request.headers.get("content-type") or "").lower()

    if content_type.startswith("application/json"):
        return await _parse_json_submission(request)

    if content_type.startswith("multipart/form-data"):
        return await _parse_multipart_submission(request)

    raise ApiError(
        status_code=400,
        error_code="INVALID_REQUEST",
        message="Request content type must be application/json or multipart/form-data.",
        details={
            "contentType": ["Use application/json or multipart/form-data."],
        },
    )


async def _parse_json_submission(request: Request) -> AnalysisSubmission:
    try:
        payload = await request.json()
    except JSONDecodeError as exc:
        raise ApiError(
            status_code=400,
            error_code="INVALID_REQUEST",
            message="Request body must be valid JSON.",
            details={"body": ["Malformed JSON request body."]},
        ) from exc

    if not isinstance(payload, dict) or not payload:
        raise ApiError(
            status_code=400,
            error_code="INVALID_REQUEST",
            message="Request payload is empty or invalid.",
            details={"body": ["Provide a JSON object with inputType and content."]},
        )

    return AnalysisSubmission(
        input_type=_coerce_string(payload.get("inputType")),
        content=_coerce_string(payload.get("content")) or _coerce_string(payload.get("text")),
    )


async def _parse_multipart_submission(request: Request) -> AnalysisSubmission:
    form = await request.form()

    if not form:
        raise ApiError(
            status_code=400,
            error_code="INVALID_REQUEST",
            message="Request payload is empty.",
            details={"body": ["Provide inputType and a valid content or file field."]},
        )

    raw_file = form.get("file")
    upload_file = raw_file if isinstance(raw_file, UploadFile) else None

    return AnalysisSubmission(
        input_type=_coerce_string(form.get("inputType")),
        content=_coerce_string(form.get("content")),
        file=upload_file,
    )


def _coerce_string(value: object | None) -> str | None:
    if isinstance(value, str):
        return value
    return None