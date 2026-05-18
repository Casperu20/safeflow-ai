"""
Pydantic models for SafeFlow AI scam analysis.

This module defines two distinct schema layers:

1. **AI Response Schema** (ScamAiResponse, EvidenceSnippetAi):
   - Represents the raw JSON contract between the AI model and the analyzer
   - Used to validate OpenAI responses
   - May evolve independently of the API contract

2. **API Response DTO** (ScamAnalysisResponse, EvidenceSnippet):
   - What the API returns to clients
   - Derived from AI response but may contain additional metadata
   - Cleaner contract for frontend consumption

This strict separation allows the AI contract to evolve independently of the API.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# AI RESPONSE SCHEMA
# ============================================================================
# Represents the raw contract with the OpenAI model.

class EvidenceSnippetAi(BaseModel):
    """
    A piece of evidence extracted from the submitted text.
    
    The model must extract only text that actually appears in the input
    and must not fabricate snippets.
    """
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Verbatim fragment from the submitted text"
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Why this fragment is suspicious"
    )
    severity: Literal["low", "medium", "high"] = Field(
        ...,
        description="Severity tier for this piece of evidence"
    )


class ScamAiResponse(BaseModel):
    """
    Raw response schema from the OpenAI scam analysis.
    
    This is the contract between the AI layer and the rest of the pipeline.
    All fields are required; the model must provide complete, valid JSON.
    
    The mapper layer will normalize the score and recompute riskLevel
    independently of what the model returned.
    """
    
    riskScore: int = Field(
        ...,
        ge=0,
        le=100,
        description="Risk score in [0, 100]"
    )
    riskLevel: Literal["low", "medium", "high"] = Field(
        ...,
        description="Risk tier (will be recomputed anyway)"
    )
    detectedScamType: Optional[str] = Field(
        ...,
        description="Detected scam category (e.g., 'invoice fraud', 'phishing') or null"
    )
    explanation: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Detailed explanation of the analysis"
    )
    indicators: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="High-level scam signals (e.g., 'urgency pressure')"
    )
    evidence: list[EvidenceSnippetAi] = Field(
        default_factory=list,
        max_length=5,
        description="Up to 5 evidence snippets from submitted text"
    )
    recommendation: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Recommended action for the end user"
    )


# ============================================================================
# API RESPONSE DTO
# ============================================================================
# What clients receive from the API.

class EvidenceSnippet(BaseModel):
    """Evidence snippet for API response."""
    
    text: str
    reason: str
    severity: Literal["low", "medium", "high"]


class ScamAnalysisResponse(BaseModel):
    """API response for scam analysis."""
    
    riskScore: int = Field(
        ...,
        ge=0,
        le=100,
        description="Normalized risk score [0, 100]"
    )
    riskLevel: Literal["low", "medium", "high"]
    detectedScamType: Optional[str] = None
    explanation: str
    indicators: list[str]
    evidence: Optional[list[EvidenceSnippet]] = None
    recommendation: str


# ============================================================================
# API REQUEST DTO
# ============================================================================

class ScamAnalysisRequest(BaseModel):
    """Request body for scam analysis endpoint."""
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=20_000,
        description="Plain text content to analyze"
    )
