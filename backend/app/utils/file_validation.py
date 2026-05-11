from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from starlette.datastructures import UploadFile

from app.schemas.errors import ApiError
from app.schemas.scam_analysis import AcceptedFileTypes


MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

_ALLOWED_FILE_RULES = {
    "pdf": {
        "mime_types": {"application/pdf"},
        "extensions": {".pdf"},
    },
    "image": {
        "mime_types": {"image/png", "image/jpeg", "image/webp"},
        "extensions": {".png", ".jpg", ".jpeg", ".webp"},
    },
}

ACCEPTED_FILE_TYPES = AcceptedFileTypes(
    pdf=["application/pdf"],
    image=["image/png", "image/jpeg", "image/webp"],
)


@dataclass(slots=True)
class ValidatedUpload:
    input_type: Literal["pdf", "image"]
    filename: str
    content_type: str
    size_bytes: int


async def validate_uploaded_file(
    upload: UploadFile | None,
    input_type: Literal["pdf", "image"],
) -> ValidatedUpload:
    if upload is None:
        raise ApiError(
            status_code=400,
            error_code="INVALID_REQUEST",
            message=f"A file is required when inputType is {input_type}.",
            details={
                "file": [f"This field is required when inputType is {input_type}."],
            },
        )

    rules = _ALLOWED_FILE_RULES[input_type]
    filename = (upload.filename or f"upload.{input_type}").strip()
    content_type = (upload.content_type or "").strip().lower()
    extension = Path(filename).suffix.lower()

    if content_type not in rules["mime_types"] or extension not in rules["extensions"]:
        raise ApiError(
            status_code=415,
            error_code="UNSUPPORTED_FILE_TYPE",
            message="Unsupported file type.",
            details={
                "file": [
                    f"Accepted MIME types for {input_type} are: {', '.join(sorted(rules['mime_types']))}."
                ]
            },
        )

    raw_bytes = await upload.read(MAX_FILE_SIZE_BYTES + 1)
    size_bytes = len(raw_bytes)
    await upload.close()

    if size_bytes == 0:
        raise ApiError(
            status_code=400,
            error_code="INVALID_REQUEST",
            message="Uploaded file cannot be empty.",
            details={"file": ["Provide a non-empty file."]},
        )

    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise ApiError(
            status_code=413,
            error_code="FILE_TOO_LARGE",
            message=f"File size must be under {MAX_FILE_SIZE_MB}MB.",
            details={"file": [f"Maximum allowed file size is {MAX_FILE_SIZE_MB}MB."]},
        )

    return ValidatedUpload(
        input_type=input_type,
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
    )