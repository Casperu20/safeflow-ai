"""
Tests for risk score normalization and risk level mapping.
"""

import pytest
from ai_service.risk_mapper import normalize_score, map_score_to_risk_level


class TestNormalizeScore:
    """Test score normalization."""
    
    def test_normalize_valid_integer(self):
        """Valid integer scores should be returned as-is."""
        assert normalize_score(0) == 0
        assert normalize_score(50) == 50
        assert normalize_score(100) == 100
    
    def test_normalize_float(self):
        """Float scores should be rounded."""
        assert normalize_score(50.4) == 50
        assert normalize_score(50.5) == 50  # Python rounds to nearest even
        assert normalize_score(50.6) == 51
    
    def test_normalize_clamps_low(self):
        """Scores below 0 should be clamped to 0."""
        assert normalize_score(-10) == 0
        assert normalize_score(-100) == 0
    
    def test_normalize_clamps_high(self):
        """Scores above 100 should be clamped to 100."""
        assert normalize_score(110) == 100
        assert normalize_score(500) == 100


class TestMapScoreToRiskLevel:
    """Test risk score to risk level mapping."""
    
    def test_low_risk(self):
        """Scores 0-39 should map to 'low'."""
        assert map_score_to_risk_level(0) == "low"
        assert map_score_to_risk_level(20) == "low"
        assert map_score_to_risk_level(39) == "low"
    
    def test_medium_risk(self):
        """Scores 40-69 should map to 'medium'."""
        assert map_score_to_risk_level(40) == "medium"
        assert map_score_to_risk_level(50) == "medium"
        assert map_score_to_risk_level(69) == "medium"
    
    def test_high_risk(self):
        """Scores 70-100 should map to 'high'."""
        assert map_score_to_risk_level(70) == "high"
        assert map_score_to_risk_level(85) == "high"
        assert map_score_to_risk_level(100) == "high"
    
    def test_boundary_conditions(self):
        """Test exact boundary values."""
        assert map_score_to_risk_level(39) == "low"
        assert map_score_to_risk_level(40) == "medium"
        assert map_score_to_risk_level(69) == "medium"
        assert map_score_to_risk_level(70) == "high"
    
    def test_invalid_score_too_low(self):
        """Scores below 0 should raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            map_score_to_risk_level(-1)
    
    def test_invalid_score_too_high(self):
        """Scores above 100 should raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            map_score_to_risk_level(101)


class TestNormalizeAndMap:
    """Integration tests for normalization and mapping."""
    
    def test_normalize_then_map_low(self):
        """Low risk scores should normalize and map correctly."""
        score = normalize_score(35.7)
        assert score == 36
        assert map_score_to_risk_level(score) == "low"
    
    def test_normalize_then_map_medium(self):
        """Medium risk scores should normalize and map correctly."""
        score = normalize_score(150)  # Clamped to 100
        assert score == 100
        assert map_score_to_risk_level(score) == "high"
        
        score = normalize_score(50.2)
        assert score == 50
        assert map_score_to_risk_level(score) == "medium"
    
    def test_normalize_then_map_high(self):
        """High risk scores should normalize and map correctly."""
        score = normalize_score(85.9)
        assert score == 86
        assert map_score_to_risk_level(score) == "high"
