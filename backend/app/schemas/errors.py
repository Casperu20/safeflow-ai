from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    errorCode: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(
            errorCode=self.error_code,
            message=self.message,
            details=self.details,
        )