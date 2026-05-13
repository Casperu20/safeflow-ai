from io import BytesIO

from pypdf import PdfReader

from app.schemas.errors import ApiError
from app.utils.file_validation import ValidatedUpload
from app.utils.text_sanitization import sanitize_text_content


def extract_text_from_pdf_upload(upload: ValidatedUpload) -> str:
    try:
        reader = PdfReader(BytesIO(upload.raw_bytes))
        extracted_text = sanitize_text_content(
            "\n".join(page.extract_text() or "" for page in reader.pages)
        )
    except Exception as exc:
        raise ApiError(
            status_code=422,
            error_code="PDF_TEXT_EXTRACTION_FAILED",
            message="Could not extract readable text from the uploaded PDF.",
            details={
                "file": [
                    "The uploaded PDF could not be parsed as a text-based document."
                ]
            },
        ) from exc

    if not extracted_text:
        raise ApiError(
            status_code=422,
            error_code="PDF_TEXT_EXTRACTION_FAILED",
            message="Could not extract readable text from the uploaded PDF.",
            details={
                "file": [
                    "The uploaded PDF does not contain extractable text. OCR is not implemented yet."
                ]
            },
        )

    return extracted_text