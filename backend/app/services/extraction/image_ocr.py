from io import BytesIO
from pathlib import Path
import shutil
import warnings

import pytesseract
from PIL import Image, ImageEnhance, ImageFile, ImageOps, UnidentifiedImageError

from app.core.config import settings
from app.schemas.errors import ApiError
from app.services.extraction.extraction_models import ExtractionResult
from app.utils.file_validation import ValidatedUpload
from app.utils.text_sanitization import normalize_extracted_text


ImageFile.LOAD_TRUNCATED_IMAGES = False

OCR_RUNTIME_UNAVAILABLE_MESSAGE = (
    "OCR is not available on the backend because Tesseract is not installed or not in PATH."
)
OCR_RUNTIME_UNAVAILABLE_DETAIL = (
    "Install Tesseract OCR on the host machine, reopen the terminal if needed, restart the backend, and retry the upload."
)


def build_ocr_runtime_unavailable_error() -> ApiError:
    return ApiError(
        status_code=503,
        error_code="OCR_RUNTIME_UNAVAILABLE",
        message=OCR_RUNTIME_UNAVAILABLE_MESSAGE,
        details={"file": [OCR_RUNTIME_UNAVAILABLE_DETAIL]},
    )


def is_ocr_runtime_available() -> bool:
    if not settings.ocr_enabled:
        return False

    tesseract_cmd = str(getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract"))
    if Path(tesseract_cmd).is_file():
        return True

    return shutil.which(tesseract_cmd) is not None


def extract_text_from_image_upload(upload: ValidatedUpload) -> ExtractionResult:
    image = _load_image(upload)
    extracted_text = perform_ocr_on_image(image, source_label=upload.filename)

    if len(extracted_text) < settings.min_extracted_text_chars:
        raise ApiError(
            status_code=422,
            error_code="EMPTY_TEXT_CONTENT",
            message="No readable text was found in this image.",
            details={
                "file": ["OCR succeeded but no readable text was found in the uploaded image."],
            },
        )

    return ExtractionResult(
        input_type="image",
        normalized_text=extracted_text,
        extraction_method="image_ocr",
        metadata={
            "width": image.width,
            "height": image.height,
            "mimeType": upload.content_type,
            "ocrLanguage": settings.ocr_lang,
        },
    )


def perform_ocr_on_image(image: Image.Image, source_label: str) -> str:
    if not settings.ocr_enabled:
        raise ApiError(
            status_code=422,
            error_code="OCR_FAILED",
            message="Could not extract readable text from this image. Please upload a clearer screenshot or paste the text manually.",
            details={
                "file": ["OCR is disabled on the backend."],
            },
        )

    if not is_ocr_runtime_available():
        raise build_ocr_runtime_unavailable_error()

    prepared_image = _prepare_image(image)

    try:
        ocr_output = pytesseract.image_to_string(
            prepared_image,
            lang=settings.ocr_lang,
            timeout=settings.ocr_timeout_seconds,
        )
    except pytesseract.TesseractNotFoundError as exc:
        raise build_ocr_runtime_unavailable_error() from exc
    except Exception as exc:
        raise ApiError(
            status_code=422,
            error_code="OCR_FAILED",
            message="Could not extract readable text from this image. Please upload a clearer screenshot or paste the text manually.",
            details={
                "file": [f"OCR failed or produced no readable text for {source_label}."],
            },
        ) from exc

    return normalize_extracted_text(ocr_output)


def _load_image(upload: ValidatedUpload) -> Image.Image:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(BytesIO(upload.raw_bytes))
            image.load()
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ApiError(
            status_code=413,
            error_code="IMAGE_TOO_LARGE",
            message="Image dimensions exceed the allowed maximum.",
            details={"file": ["The uploaded image is too large to process safely."]},
        ) from exc
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ApiError(
            status_code=422,
            error_code="CORRUPTED_FILE",
            message="The uploaded image is corrupted or unreadable.",
            details={"file": ["The uploaded image could not be opened."]},
        ) from exc

    if image.width > settings.max_image_width or image.height > settings.max_image_height:
        raise ApiError(
            status_code=413,
            error_code="IMAGE_TOO_LARGE",
            message="Image dimensions exceed the allowed maximum.",
            details={
                "file": [
                    f"Maximum allowed dimensions are {settings.max_image_width}x{settings.max_image_height}px."
                ]
            },
        )

    return image


def _prepare_image(image: Image.Image) -> Image.Image:
    prepared = image.convert("L")
    prepared = ImageOps.autocontrast(prepared)
    prepared = ImageEnhance.Contrast(prepared).enhance(1.4)

    if min(prepared.size) < 700:
        scale = max(2, int(700 / max(1, min(prepared.size))))
        prepared = prepared.resize(
            (prepared.width * scale, prepared.height * scale),
            Image.Resampling.LANCZOS,
        )

    return prepared