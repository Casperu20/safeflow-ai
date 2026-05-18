"""
Risk score normalization and risk level mapping.

Thresholds are centralized here so that future work (e.g., per-channel tuning
or A/B threshold experiments) only needs to change this one place.
"""

from typing import Literal


# Risk level thresholds
RISK_THRESHOLDS = {
    "LOW_MAX": 39,
    "MEDIUM_MAX": 69,
}


def normalize_score(raw: float | int) -> int:
    """
    Clamp an arbitrary number to the valid [0, 100] integer range.
    
    Used as a defensive step before calling map_score_to_risk_level when the
    score source (e.g., a future LightGBM model) may return floats or
    out-of-range values.
    
    Args:
        raw: Arbitrary numeric risk score
    
    Returns:
        Normalized integer in [0, 100]
    """
    return int(round(min(100, max(0, raw))))


def map_score_to_risk_level(
    score: int,
) -> Literal["low", "medium", "high"]:
    """
    Map a normalized risk score to the corresponding risk level.
    
    Thresholds:
    - 0–39 → low
    - 40–69 → medium
    - 70–100 → high
    
    Args:
        score: Normalized risk score in [0, 100]
    
    Returns:
        Risk level ("low", "medium", or "high")
    
    Raises:
        RangeError: If score is outside [0, 100]
    """
    if score < 0 or score > 100:
        raise ValueError(
            f"Risk score must be between 0 and 100, received: {score}"
        )
    
    if score <= RISK_THRESHOLDS["LOW_MAX"]:
        return "low"
    elif score <= RISK_THRESHOLDS["MEDIUM_MAX"]:
        return "medium"
    else:
        return "high"
