from dataclasses import dataclass, field
from typing import Any, Literal

from starlette.datastructures import UploadFile

from app.schemas.scam_analysis import ExtractionMethod, InputType


@dataclass(slots=True)
class AnalysisSubmission:
    input_type: str | None
    content: str | None = None
    file: UploadFile | None = None


@dataclass(slots=True)
class ExtractionPageResult:
    page_number: int
    method: ExtractionMethod
    extracted_character_count: int


@dataclass(slots=True)
class ExtractionResult:
    input_type: InputType
    normalized_text: str
    extraction_method: ExtractionMethod
    warnings: list[str] = field(default_factory=list)
    page_count: int | None = None
    page_results: list[ExtractionPageResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)