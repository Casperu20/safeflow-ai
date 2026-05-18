"""
Business logic service for scam analysis.

Handles input validation, error wrapping, response formatting,
and orchestration between the analyzer and API layers.
"""

import logging
import uuid
from typing import Optional

from .analyzer import ScamAiAnalyzer
from .schemas import ScamAnalysisResponse, EvidenceSnippet
from .errors import ScamAiAnalysisError, ScamAnalysisError, ScamAnalysisErrorCode
from .security import validate_analysis_input, safe_log_analysis_request


logger = logging.getLogger(__name__)


class ScamAnalysisService:
    """
    High-level service for scam analysis.
    
    Responsibilities:
    - Validate input
    - Call the AI analyzer
    - Handle and wrap errors
    - Format response DTOs
    """
    
    def __init__(self, analyzer: ScamAiAnalyzer):
        """
        Initialize the service.
        
        Args:
            analyzer: ScamAiAnalyzer instance for AI operations
        """
        self.analyzer = analyzer
    
    async def analyze_text(self, content: str) -> ScamAnalysisResponse:
        """
        Analyze text for scam risk.
        
        Process:
        1. Validate input (non-empty, within size limits)
        2. Call AI analyzer
        3. Format response DTO
        4. Handle and wrap errors appropriately
        
        Args:
            content: User-submitted text to analyze
        
        Returns:
            Formatted ScamAnalysisResponse
        
        Raises:
            ScamAnalysisError: With appropriate error code and HTTP status
        """
        # Validate input
        try:
            validate_analysis_input(content)
        except ValueError as err:
            raise ScamAnalysisError(
                ScamAnalysisErrorCode.EMPTY_TEXT_CONTENT,
                "Submitted text content must not be empty.",
                400,
            )
        
        # Log request (safe, truncated preview only)
        logger.info(safe_log_analysis_request(content))
        
        # Call analyzer
        try:
            ai_response = await self.analyzer.analyze_text(content)
        except ScamAiAnalysisError as err:
            logger.error(f"AI analysis error: {err.message}", exc_info=err.cause)
            raise ScamAnalysisError(
                ScamAnalysisErrorCode.ANALYSIS_FAILED,
                "Scam analysis could not be completed. Please try again.",
                502,
            )
        except Exception as err:
            logger.error(f"Unexpected error during analysis", exc_info=err)
            raise ScamAnalysisError(
                ScamAnalysisErrorCode.SERVER_ERROR,
                "An unexpected error occurred during analysis.",
                500,
            )
        
        # Format response DTO
        # Include evidence only if present, detectedScamType only if not None
        evidence: Optional[list[EvidenceSnippet]] = None
        if ai_response.evidence and len(ai_response.evidence) > 0:
            evidence = [
                EvidenceSnippet(
                    text=snippet.text,
                    reason=snippet.reason,
                    severity=snippet.severity,
                )
                for snippet in ai_response.evidence
            ]
        
        detected_scam_type: Optional[str] = None
        if ai_response.detectedScamType is not None:
            detected_scam_type = ai_response.detectedScamType
        
        response = ScamAnalysisResponse(
            riskScore=ai_response.riskScore,
            riskLevel=ai_response.riskLevel,
            detectedScamType=detected_scam_type,
            explanation=ai_response.explanation,
            indicators=ai_response.indicators,
            evidence=evidence,
            recommendation=ai_response.recommendation,
        )
        
        logger.info(
            f"Analysis completed successfully: "
            f"riskScore={ai_response.riskScore}, "
            f"riskLevel={ai_response.riskLevel}"
        )
        
        return response
