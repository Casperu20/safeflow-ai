from typing import cast

from app.core.config import settings
from app.schemas.errors import ApiError
from app.schemas.scam_analysis import InputType
from app.services.extraction.extraction_models import AnalysisSubmission, ExtractionResult
from app.services.extraction.image_ocr import extract_text_from_image_upload
from app.services.extraction.pdf_extraction import extract_text_from_pdf_upload
from app.utils.file_validation import validate_uploaded_file
from app.utils.text_sanitization import normalize_extracted_text


SUPPORTED_INPUT_TYPES = {"text", "pdf", "image"}


class DocumentExtractionService:
    async def extract(self, submission: AnalysisSubmission) -> ExtractionResult:
        input_type = self._validate_input_type(submission.input_type)

        if input_type == "text":
            return self._extract_text(submission)

        if input_type == "pdf":
            return await self._extract_pdf(submission)

        return await self._extract_image(submission)

    def _validate_input_type(self, input_type: str | None) -> InputType:
        if input_type not in SUPPORTED_INPUT_TYPES:
            raise ApiError(
                status_code=400,
                error_code="INVALID_INPUT_TYPE",
                message="inputType must be one of: text, pdf, image.",
                details={
                    "inputType": ["Allowed values are text, pdf, image."],
                },
            )

        return cast(InputType, input_type)

    def _extract_text(self, submission: AnalysisSubmission) -> ExtractionResult:
        if submission.file is not None:
            raise ApiError(
                status_code=400,
                error_code="INVALID_REQUEST",
                message="Text analysis accepts content only.",
                details={
                    "file": ["Do not upload a file when inputType is text."],
                },
            )

        content = normalize_extracted_text(submission.content or "")
        if not content:
            raise ApiError(
                status_code=400,
                error_code="EMPTY_TEXT_CONTENT",
                message="Text content cannot be empty.",
                details={
                    "content": ["This field is required when inputType is text."],
                },
            )

        if len(content) > settings.max_text_length:
            raise ApiError(
                status_code=400,
                error_code="CONTENT_TOO_LONG",
                message=f"Text content must be {settings.max_text_length} characters or less.",
                details={
                    "content": [f"Maximum length is {settings.max_text_length} characters."],
                },
            )

        return ExtractionResult(
            input_type="text",
            normalized_text=content,
            extraction_method="plain_text",
        )

    async def _extract_pdf(self, submission: AnalysisSubmission) -> ExtractionResult:
        if normalize_extracted_text(submission.content or ""):
            raise ApiError(
                status_code=400,
                error_code="INVALID_REQUEST",
                message="PDF analysis accepts file uploads only.",
                details={
                    "content": ["Do not send content when inputType is pdf."],
                },
            )

        validated_upload = await validate_uploaded_file(submission.file, "pdf")
        return extract_text_from_pdf_upload(validated_upload)

    async def _extract_image(self, submission: AnalysisSubmission) -> ExtractionResult:
        if normalize_extracted_text(submission.content or ""):
            raise ApiError(
                status_code=400,
                error_code="INVALID_REQUEST",
                message="Image analysis accepts file uploads only.",
                details={
                    "content": ["Do not send content when inputType is image."],
                },
            )

        validated_upload = await validate_uploaded_file(submission.file, "image")
        return extract_text_from_image_upload(validated_upload)