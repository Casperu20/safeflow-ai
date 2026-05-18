from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.scam_analysis import EvidenceItem, InputType, RiskLevel


class AnalysisHistoryItemResponse(BaseModel):
    analysisId: str
    inputType: InputType
    originalFilename: str | None = None
    inputPreview: str | None = None
    riskScore: int = Field(ge=0, le=100)
    riskLevel: RiskLevel
    detectedScamType: str | None = None
    explanation: str
    indicators: list[str] = Field(default_factory=list)
    recommendation: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    extractionMethod: str | None = None
    analysisMode: str | None = None
    createdAt: datetime


class AnalysisHistoryListResponse(BaseModel):
    items: list[AnalysisHistoryItemResponse] = Field(default_factory=list)
    total: int = 0
    limit: int = 20
    offset: int = 0