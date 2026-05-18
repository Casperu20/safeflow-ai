"""
Security utilities for SafeFlow AI.

Includes input validation, prompt injection defenses, and safe logging.
"""

import logging
import re
from typing import Optional


logger = logging.getLogger(__name__)


def validate_analysis_input(text: str) -> None:
    """
    Validate user input before sending to AI model.
    
    Checks for:
    - Empty or whitespace-only content
    - Content length limits
    
    Args:
        text: User-supplied text to analyze
    
    Raises:
        ValueError: If input fails validation
    """
    if not text or not text.strip():
        raise ValueError("Text content must not be empty or whitespace-only")
    
    if len(text) > 20_000:
        raise ValueError(f"Text content exceeds maximum length of 20,000 characters")


def safe_log_analysis_request(text: str, text_preview_length: int = 50) -> str:
    """
    Create a safe, truncated preview of submitted text for logging.
    
    Never logs the full user-submitted text to avoid leaking PII or sensitive data.
    
    Args:
        text: User-submitted text
        text_preview_length: Number of characters to include in preview
    
    Returns:
        Safe preview string for logging (e.g., "Text submission (125 chars): 'First 50 ch...'")
    """
    text_length = len(text)
    preview = text[:text_preview_length]
    
    # Sanitize preview: remove newlines and replace with spaces
    preview = preview.replace("\n", " ").replace("\r", " ")
    
    if text_length > text_preview_length:
        preview = preview.rstrip() + "..."
    
    return f"Text submission ({text_length} chars): '{preview}'"


def is_likely_prompt_injection(text: str) -> bool:
    """
    Heuristic detector for obvious prompt injection attempts.
    
    This is a defense-in-depth measure. The system prompt is the primary defense.
    
    This function checks for common injection patterns:
    - "Ignore previous instructions"
    - "New instructions:"
    - "System prompt:"
    - Other common jailbreak patterns
    
    Args:
        text: Text to check
    
    Returns:
        True if text matches known injection patterns, False otherwise
    """
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    injection_patterns = [
        r"ignore\s+previous\s+instructions?",
        r"(new|updated|secret|hidden)\s+instructions?",
        r"system\s+prompt",
        r"disregard\s+.*instructions?",
        r"forget\s+.*instructions?",
        r"override\s+.*settings?",
        r"take\s+control",
        r"jailbreak",
        r"you\s+are\s+now",
        r"role\s+play\s+as",
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False
