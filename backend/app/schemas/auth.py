from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, TypeAdapter, model_validator


_email_adapter = TypeAdapter(EmailStr)


def normalize_email(value: str) -> str:
    return str(_email_adapter.validate_python((value or "").strip().lower()))


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    fullName: str | None = None
    role: str
    createdAt: datetime | None = None


class AuthResponse(BaseModel):
    user: UserResponse
    accessToken: str
    tokenType: str = "bearer"


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    email: str | None = None
    username: str | None = None
    password: str = Field(min_length=8)
    fullName: str | None = None

    @model_validator(mode="after")
    def normalize(self) -> Self:
        email_candidate = self.email or self.username
        if not email_candidate:
            raise ValueError("Email is required.")

        self.email = normalize_email(email_candidate)
        display_name = self.fullName or self.username
        self.fullName = display_name.strip() if display_name and display_name.strip() else None
        return self


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    email: str | None = None
    username: str | None = None
    password: str = Field(min_length=1)

    @model_validator(mode="after")
    def normalize(self) -> Self:
        email_candidate = self.email or self.username
        if not email_candidate:
            raise ValueError("Email is required.")

        self.email = normalize_email(email_candidate)
        return self


class RecoverPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    email: str

    @model_validator(mode="after")
    def normalize(self) -> Self:
        self.email = normalize_email(self.email)
        return self


class SuccessResponse(BaseModel):
    success: bool = True
    message: str | None = None