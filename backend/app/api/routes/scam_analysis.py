import logging
from json import JSONDecodeError
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from app.api.dependencies.auth import get_optional_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.errors import ApiError, ErrorResponse
from app.schemas.scam_analysis import ScamAnalysisConfigResponse, ScamAnalysisResponse
from app.services.ai_service_client import AiServiceClient
from app.services.extraction.document_extraction_service import DocumentExtractionService
from app.services.extraction.extraction_models import AnalysisSubmission
from app.services.history_service import history_service
from app.services.scam_analysis_service import ScamAnalysisService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/scam-analysis", tags=["scam-analysis"])
ai_service_client = AiServiceClient()
extraction_service = DocumentExtractionService()
service = ScamAnalysisService(ai_service_client)


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
        401: {"model": ErrorResponse},
        402: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_scam_submission(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> ScamAnalysisResponse:
    submission = await _parse_submission(request)

    try:
        extracted_content = await extraction_service.extract(submission)
        analysis_response = await service.analyze_extracted_text(extracted_content)

        if not analysis_response.analysisId:
            analysis_response.analysisId = f"analysis_{uuid4()}"

        if current_user is not None:
            history_service.create_history_record(
                db,
                user=current_user,
                submission=submission,
                extraction=extracted_content,
                analysis_response=analysis_response,
            )

        return analysis_response
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
