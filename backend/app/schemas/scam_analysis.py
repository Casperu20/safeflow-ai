from typing import Literal

from pydantic import BaseModel, Field


InputType = Literal["text", "pdf", "image"]
RiskLevel = Literal["low", "medium", "high"]
EvidenceSeverity = Literal["low", "medium", "high"]


class EvidenceItem(BaseModel):
    text: str
    reason: str
    severity: EvidenceSeverity


class AiServiceResponse(BaseModel):
    """Response from the AI service microservice."""
    riskScore: int = Field(ge=0, le=100)
    riskLevel: RiskLevel
    detectedScamType: str | None = None
    explanation: str
    indicators: list[str] = Field(default_factory=list)
    recommendation: str
    evidence: list[EvidenceItem] = Field(default_factory=list)


class ScamAnalysisResponse(BaseModel):
    analysisId: str | None = Field(default=None, pattern=r"^analysis_[0-9a-fA-F-]+$")
    riskScore: int = Field(ge=0, le=100)
    riskLevel: RiskLevel
    detectedScamType: str | None = None
    explanation: str
    indicators: list[str] = Field(default_factory=list)
    recommendation: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    analysisMode: Literal["mock", "ai"] | None = None


class AcceptedFileTypes(BaseModel):
    pdf: list[str]
    image: list[str]


class AnalysisLimits(BaseModel):
    maxTextLength: int
    maxFileSizeMB: int
    maxPdfPages: int | None


class RiskThresholds(BaseModel):
    low: list[int]
    medium: list[int]
    high: list[int]


class ScamAnalysisConfigResponse(BaseModel):
    inputTypes: list[InputType]
    acceptedFileTypes: AcceptedFileTypes
    limits: AnalysisLimits
    riskThresholds: RiskThresholds
    processingMode: Literal["synchronous"] = "synchronous"
    analysisMode: Literal["mock", "ai", "hybrid"] = "hybrid"