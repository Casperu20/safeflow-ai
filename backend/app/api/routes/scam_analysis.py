from json import JSONDecodeError
from uuid import uuid4
import logging

from fastapi import APIRouter, Request
from starlette.datastructures import UploadFile

from app.schemas.errors import ApiError, ErrorResponse
from app.schemas.scam_analysis import AiServiceResponse, ScamAnalysisConfigResponse, ScamAnalysisResponse
from app.services.ai_service_client import AiServiceClient
from app.services.scam_analysis_service import AnalysisSubmission, ScamAnalysisService
from app.utils.file_validation import validate_uploaded_file
from app.utils.pdf_extraction import extract_text_from_pdf_upload
from app.utils.text_sanitization import sanitize_text_content

logger = logging.getLogger(__name__)

MAX_AI_INPUT_CHARS = 20_000


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
            return await _analyze_text_submission(submission)

        if submission.input_type == "pdf":
            return await _analyze_pdf_submission(submission)

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


async def _analyze_text_submission(submission: AnalysisSubmission) -> ScamAnalysisResponse:
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

    return await _analyze_with_ai(_prepare_ai_input(content))


async def _analyze_pdf_submission(submission: AnalysisSubmission) -> ScamAnalysisResponse:
    if sanitize_text_content(submission.content or ""):
        raise ApiError(
            status_code=400,
            error_code="INVALID_REQUEST",
            message="PDF analysis accepts file uploads only.",
            details={
                "content": ["Do not send content when inputType is pdf."],
            },
        )

    validated_upload = await validate_uploaded_file(submission.file, "pdf")
    extracted_text = extract_text_from_pdf_upload(validated_upload)
    return await _analyze_with_ai(_prepare_ai_input(extracted_text))


async def _analyze_with_ai(content: str) -> ScamAnalysisResponse:
    ai_response = AiServiceResponse.model_validate(
        await ai_service_client.analyze_text(content)
    )
    logger.info(
        "AI analysis completed with riskScore=%s riskLevel=%s",
        ai_response.riskScore,
        ai_response.riskLevel,
    )
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


def _prepare_ai_input(content: str) -> str:
    sanitized_content = sanitize_text_content(content)

    if len(sanitized_content) <= MAX_AI_INPUT_CHARS:
        return sanitized_content

    # Keep the AI request within the ai_service validation limit and reduce long-PDF latency.
    return sanitized_content[:MAX_AI_INPUT_CHARS].rstrip()