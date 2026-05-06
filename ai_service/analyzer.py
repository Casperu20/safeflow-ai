"""
AI analyzer for scam detection.

Handles OpenAI API calls, response parsing, validation, and score normalization.
Maintains strict separation between what the AI returns and what we expose to the API.
"""

import json
import logging
from openai import OpenAI
from pydantic import ValidationError

from .schemas import ScamAiResponse
from .prompts import (
    SCAM_ANALYSIS_SYSTEM_PROMPT,
    build_scam_analysis_user_prompt,
)
from .risk_mapper import normalize_score, map_score_to_risk_level
from .errors import ScamAiAnalysisError


logger = logging.getLogger(__name__)


class ScamAiAnalyzer:
    """
    Analyzes text for scam risk using OpenAI's GPT model.
    
    Responsibilities:
    - Call OpenAI API with structured prompts
    - Parse and validate JSON responses
    - Normalize risk scores to [0, 100]
    - Recompute risk level (never trust model's riskLevel)
    - Handle and wrap errors appropriately
    """
    
    def __init__(self, openai_client: OpenAI):
        """
        Initialize the analyzer.
        
        Args:
            openai_client: Configured OpenAI client instance
        """
        self.openai = openai_client
    
    async def analyze_text(self, input_text: str) -> ScamAiResponse:
        """
        Analyze text for scam risk.
        
        Process:
        1. Call OpenAI API with system and user prompts
        2. Parse returned JSON
        3. Validate against ScamAiResponseSchema
        4. Normalize riskScore to [0, 100]
        5. Recompute riskLevel from normalized score
        6. Return validated response
        
        Args:
            input_text: User-submitted text to analyze
        
        Returns:
            Validated and normalized ScamAiResponse
        
        Raises:
            ScamAiAnalysisError: If OpenAI call fails, returns invalid JSON,
                                 or validation fails
        """
        raw_content: str
        
        # Call OpenAI API
        try:
            completion = self.openai.chat.completions.create(
                model="gpt-4.1-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SCAM_ANALYSIS_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_scam_analysis_user_prompt(input_text),
                    },
                ],
            )
            
            raw_content = completion.choices[0].message.content or ""
        except Exception as err:
            raise ScamAiAnalysisError(
                "OpenAI request failed",
                cause=err,
            )
        
        # Parse JSON
        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError as err:
            raise ScamAiAnalysisError(
                "OpenAI returned invalid JSON — treating as analysis failure",
                cause=err,
            )
        
        # Validate schema
        try:
            result = ScamAiResponse(**parsed)
        except ValidationError as err:
            raise ScamAiAnalysisError(
                f"OpenAI response failed schema validation: {err}",
                cause=err,
            )
        
        # Normalize score and recompute risk level
        # IMPORTANT: Never trust the model's riskLevel field.
        # The score is the authoritative value; riskLevel is derived from it.
        normalized_score = normalize_score(result.riskScore)
        recomputed_risk_level = map_score_to_risk_level(normalized_score)
        
        # Return normalized response
        return ScamAiResponse(
            riskScore=normalized_score,
            riskLevel=recomputed_risk_level,
            detectedScamType=result.detectedScamType,
            explanation=result.explanation,
            indicators=result.indicators,
            evidence=result.evidence,
            recommendation=result.recommendation,
        )
