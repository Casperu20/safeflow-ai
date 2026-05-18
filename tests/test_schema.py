"""
Tests for Pydantic schemas and validation.
"""

import pytest
from pydantic import ValidationError

from ai_service.schemas import (
    ScamAnalysisRequest,
    ScamAnalysisResponse,
    EvidenceSnippet,
    ScamAiResponse,
    EvidenceSnippetAi,
)


class TestScamAnalysisRequest:
    """Test request schema validation."""
    
    def test_valid_request(self):
        """Valid requests should parse correctly."""
        req = ScamAnalysisRequest(text="This is a test message")
        assert req.text == "This is a test message"
    
    def test_empty_text_fails(self):
        """Empty text should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ScamAnalysisRequest(text="")
        assert "at least 1 character" in str(exc_info.value).lower()
    
    def test_text_exceeds_max_length(self):
        """Text exceeding 20,000 characters should fail."""
        long_text = "x" * 20_001
        with pytest.raises(ValidationError) as exc_info:
            ScamAnalysisRequest(text=long_text)
        assert "max_length" in str(exc_info.value).lower() or "20000" in str(exc_info.value)
    
    def test_text_at_max_length(self):
        """Text at exactly 20,000 characters should pass."""
        max_text = "x" * 20_000
        req = ScamAnalysisRequest(text=max_text)
        assert len(req.text) == 20_000


class TestEvidenceSnippet:
    """Test evidence snippet schema."""
    
    def test_valid_snippet(self):
        """Valid evidence snippets should parse correctly."""
        evidence = EvidenceSnippet(
            text="Please wire $10,000 urgently",
            reason="Contains urgency pressure and payment request",
            severity="high",
        )
        assert evidence.text == "Please wire $10,000 urgently"
        assert evidence.severity == "high"
    
    def test_invalid_severity(self):
        """Invalid severity should fail."""
        with pytest.raises(ValidationError):
            EvidenceSnippet(
                text="Some text",
                reason="Some reason",
                severity="critical",  # Invalid
            )


class TestScamAnalysisResponse:
    """Test API response schema."""
    
    def test_valid_response_minimal(self):
        """Minimal valid response should parse."""
        response = ScamAnalysisResponse(
            riskScore=45,
            riskLevel="medium",
            explanation="Detected urgency pressure",
            indicators=["urgency"],
            recommendation="Do not wire funds immediately",
        )
        assert response.riskScore == 45
        assert response.riskLevel == "medium"
        assert response.detectedScamType is None
        assert response.evidence is None
    
    def test_valid_response_full(self):
        """Full response with all optional fields should parse."""
        response = ScamAnalysisResponse(
            riskScore=75,
            riskLevel="high",
            detectedScamType="invoice fraud",
            explanation="Detected invoice fraud",
            indicators=["urgency", "authority impersonation"],
            evidence=[
                EvidenceSnippet(
                    text="Pay invoice immediately",
                    reason="Urgency pressure",
                    severity="high",
                )
            ],
            recommendation="Verify invoice with known supplier",
        )
        assert response.riskScore == 75
        assert response.detectedScamType == "invoice fraud"
        assert len(response.evidence) == 1
    
    def test_risk_score_out_of_range(self):
        """Risk score outside [0, 100] should fail."""
        with pytest.raises(ValidationError) as exc_info:
            ScamAnalysisResponse(
                riskScore=150,
                riskLevel="high",
                explanation="Test",
                indicators=[],
                recommendation="Test",
            )
        assert "less than or equal to 100" in str(exc_info.value).lower()


class TestEvidenceSnippetAi:
    """Test AI response evidence snippet schema."""
    
    def test_valid_ai_evidence(self):
        """Valid AI evidence should parse."""
        evidence = EvidenceSnippetAi(
            text="Click here immediately",
            reason="Suspicious link with urgency",
            severity="medium",
        )
        assert evidence.text == "Click here immediately"
    
    def test_text_exceeds_max_length(self):
        """Evidence text exceeding 500 chars should fail."""
        long_text = "x" * 501
        with pytest.raises(ValidationError):
            EvidenceSnippetAi(
                text=long_text,
                reason="Some reason",
                severity="high",
            )


class TestScamAiResponse:
    """Test AI response schema."""
    
    def test_valid_ai_response_minimal(self):
        """Minimal valid AI response should parse."""
        response = ScamAiResponse(
            riskScore=35,
            riskLevel="low",
            detectedScamType=None,
            explanation="No indicators detected",
            indicators=[],
            evidence=[],
            recommendation="Message appears legitimate",
        )
        assert response.riskScore == 35
        assert response.detectedScamType is None
        assert len(response.indicators) == 0
    
    def test_valid_ai_response_full(self):
        """Full AI response should parse."""
        response = ScamAiResponse(
            riskScore=82,
            riskLevel="high",
            detectedScamType="phishing",
            explanation="Multiple phishing indicators detected",
            indicators=["link spoofing", "urgency", "impersonation"],
            evidence=[
                EvidenceSnippetAi(
                    text="Verify account details",
                    reason="Phishing request",
                    severity="high",
                ),
                EvidenceSnippetAi(
                    text="Click here now",
                    reason="Urgency pressure",
                    severity="medium",
                ),
            ],
            recommendation="Do not click links or enter credentials",
        )
        assert response.riskScore == 82
        assert response.detectedScamType == "phishing"
        assert len(response.evidence) == 2
    
    def test_evidence_exceeds_max_count(self):
        """More than 5 evidence items should fail."""
        with pytest.raises(ValidationError) as exc_info:
            ScamAiResponse(
                riskScore=50,
                riskLevel="medium",
                detectedScamType=None,
                explanation="Test",
                indicators=[],
                evidence=[
                    EvidenceSnippetAi(
                        text=f"Evidence {i}",
                        reason="Test",
                        severity="low",
                    )
                    for i in range(6)  # 6 items, exceeds max of 5
                ],
                recommendation="Test",
            )
        assert "max_items" in str(exc_info.value).lower() or "5" in str(exc_info.value)
    
    def test_indicators_exceeds_max_count(self):
        """More than 20 indicators should fail."""
        with pytest.raises(ValidationError):
            ScamAiResponse(
                riskScore=50,
                riskLevel="medium",
                detectedScamType=None,
                explanation="Test",
                indicators=[f"indicator-{i}" for i in range(21)],  # 21 items
                evidence=[],
                recommendation="Test",
            )


class TestSchemaIntegration:
    """Integration tests for schema interactions."""
    
    def test_ai_response_to_api_response_conversion(self):
        """AI response should be convertible to API response."""
        ai_response = ScamAiResponse(
            riskScore=55,
            riskLevel="medium",
            detectedScamType="social engineering",
            explanation="Detected social engineering",
            indicators=["authority claim"],
            evidence=[
                EvidenceSnippetAi(
                    text="I'm your bank",
                    reason="Authority impersonation",
                    severity="high",
                )
            ],
            recommendation="Verify caller independently",
        )
        
        # Convert to API response
        api_response = ScamAnalysisResponse(
            riskScore=ai_response.riskScore,
            riskLevel=ai_response.riskLevel,
            detectedScamType=ai_response.detectedScamType,
            explanation=ai_response.explanation,
            indicators=ai_response.indicators,
            evidence=[
                EvidenceSnippet(
                    text=e.text,
                    reason=e.reason,
                    severity=e.severity,
                )
                for e in ai_response.evidence
            ] if ai_response.evidence else None,
            recommendation=ai_response.recommendation,
        )
        
        assert api_response.riskScore == 55
        assert api_response.riskLevel == "medium"
        assert api_response.detectedScamType == "social engineering"
