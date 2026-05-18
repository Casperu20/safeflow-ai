"""
Error handling for SafeFlow AI scam analysis.

Defines custom exceptions and error codes that match the TypeScript implementation.
"""

from enum import Enum
from typing import Optional


class ScamAnalysisErrorCode(str, Enum):
    """Error codes for scam analysis failures."""
    
    INVALID_INPUT_TYPE = "INVALID_INPUT_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    PDF_TEXT_EXTRACTION_FAILED = "PDF_TEXT_EXTRACTION_FAILED"
    OCR_FAILED = "OCR_FAILED"
    EMPTY_TEXT_CONTENT = "EMPTY_TEXT_CONTENT"
    CONTENT_TOO_LONG = "CONTENT_TOO_LONG"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    SERVER_ERROR = "SERVER_ERROR"


class ScamAnalysisError(Exception):
    """
    Custom exception for scam analysis failures.
    
    Maps to HTTP error responses with structured error information.
    """
    
    def __init__(
        self,
        error_code: ScamAnalysisErrorCode,
        message: str,
        status_code: int,
        details: Optional[dict[str, list[str]]] = None,
    ):
        """
        Initialize a ScamAnalysisError.
        
        Args:
            error_code: Machine-readable error code
            message: Human-readable error message
            status_code: HTTP status code to return
            details: Optional structured validation details
        """
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)
    
    def to_api_error_dict(self) -> dict:
        """
        Serialize to API error response.
        
        Returns a dictionary suitable for JSON response body.
        """
        result = {
            "errorCode": self.error_code.value,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class ScamAiAnalysisError(Exception):
    """
    Error that occurs during AI model interaction or response parsing.
    
    This is an internal error that gets wrapped in a ScamAnalysisError
    for the API response.
    """
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        """
        Initialize a ScamAiAnalysisError.
        
        Args:
            message: Description of what went wrong
            cause: Optional underlying exception
        """
        self.message = message
        self.cause = cause
        super().__init__(self.message)
