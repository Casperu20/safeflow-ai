from io import BytesIO

import fitz
from PIL import Image

from app.core.config import settings
from app.schemas.errors import ApiError
from app.services.extraction import image_ocr
from app.services.extraction.extraction_models import ExtractionPageResult, ExtractionResult
from app.utils.file_validation import ValidatedUpload
from app.utils.text_sanitization import normalize_extracted_text, safe_text_excerpt


def extract_text_from_pdf_upload(upload: ValidatedUpload) -> ExtractionResult:
    try:
        document = fitz.open(stream=upload.raw_bytes, filetype="pdf")
    except Exception as exc:
        raise ApiError(
            status_code=422,
            error_code="CORRUPTED_FILE",
            message="The uploaded PDF is corrupted or unreadable.",
            details={"file": ["The uploaded PDF could not be opened."]},
        ) from exc

    with document:
        if document.needs_pass:
            raise ApiError(
                status_code=422,
                error_code="PDF_ENCRYPTED",
                message="This PDF is password-protected and cannot be analyzed.",
                details={"file": ["Encrypted or password-protected PDFs are not supported."]},
            )

        if document.page_count > settings.max_pdf_pages:
            raise ApiError(
                status_code=422,
                error_code="PDF_TOO_MANY_PAGES",
                message="This PDF has too many pages to analyze.",
                details={
                    "file": [f"Maximum allowed PDF pages is {settings.max_pdf_pages}."]
                },
            )

        page_texts: list[str] = []
        page_results: list[ExtractionPageResult] = []
        warnings: list[str] = []
        ocr_runtime_unavailable = False

        for page_number in range(document.page_count):
            page = document.load_page(page_number)
            text_layer = normalize_extracted_text(page.get_text("text"))
            ocr_text = ""

            if len(text_layer) < settings.min_extracted_text_chars and settings.ocr_enabled:
                rendered_image = _render_page_to_image(page)
                try:
                    ocr_text = image_ocr.perform_ocr_on_image(
                        rendered_image,
                        source_label=f"{upload.filename} page {page_number + 1}",
                    )
                except ApiError as exc:
                    if exc.error_code == "OCR_RUNTIME_UNAVAILABLE":
                        ocr_runtime_unavailable = True
                    warnings.append(
                        f"OCR could not extract text from page {page_number + 1}: {exc.error_code}."
                    )

            combined_text = _combine_page_text(text_layer, ocr_text)
            if combined_text:
                page_texts.append(combined_text)

            page_results.append(
                ExtractionPageResult(
                    page_number=page_number + 1,
                    method=_resolve_page_method(text_layer, ocr_text),
                    extracted_character_count=len(combined_text),
                )
            )

        full_text = normalize_extracted_text("\n\n".join(page_texts))
        if not full_text:
            if ocr_runtime_unavailable:
                raise image_ocr.build_ocr_runtime_unavailable_error()

            raise ApiError(
                status_code=422,
                error_code="PDF_TEXT_EXTRACTION_FAILED",
                message="Could not extract readable text from this PDF. Please upload a clearer document or paste the text manually.",
                details={
                    "file": [
                        "The uploaded PDF does not contain extractable text. OCR is not implemented or did not produce readable text."
                    ]
                },
            )

        return ExtractionResult(
            input_type="pdf",
            normalized_text=full_text,
            extraction_method=_resolve_document_method(page_results),
            warnings=warnings,
            page_count=document.page_count,
            page_results=page_results,
            metadata=_extract_safe_pdf_metadata(document.metadata or {}),
        )


def _render_page_to_image(page: fitz.Page) -> Image.Image:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    image = Image.open(BytesIO(pixmap.tobytes("png")))
    image.load()
    return image


def _combine_page_text(text_layer: str, ocr_text: str) -> str:
    if not text_layer:
        return ocr_text
    if not ocr_text:
        return text_layer

    lower_text_layer = text_layer.casefold()
    lower_ocr_text = ocr_text.casefold()

    if lower_text_layer == lower_ocr_text:
        return text_layer
    if lower_text_layer in lower_ocr_text:
        return ocr_text
    if lower_ocr_text in lower_text_layer:
        return text_layer

    return normalize_extracted_text(f"{text_layer}\n{ocr_text}")


def _resolve_page_method(text_layer: str, ocr_text: str) -> str:
    if text_layer and ocr_text:
        return "pdf_hybrid"
    if ocr_text:
        return "pdf_ocr"
    return "pdf_text_layer"


def _resolve_document_method(page_results: list[ExtractionPageResult]) -> str:
    methods = {page.method for page in page_results if page.extracted_character_count > 0}
    if not methods:
        return "pdf_ocr"
    if methods == {"pdf_text_layer"}:
        return "pdf_text_layer"
    if methods == {"pdf_ocr"}:
        return "pdf_ocr"
    return "pdf_hybrid"


def _extract_safe_pdf_metadata(metadata: dict[str, str]) -> dict[str, str]:
    safe_metadata: dict[str, str] = {}

    for key in ("title", "author", "subject"):
        value = normalize_extracted_text(metadata.get(key, ""))
        if value:
            safe_metadata[key] = safe_text_excerpt(value, max_length=80)

    return safe_metadata