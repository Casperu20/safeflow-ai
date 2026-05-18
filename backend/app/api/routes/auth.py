from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RecoverPasswordRequest,
    RegisterRequest,
    SuccessResponse,
    UserResponse,
)
from app.schemas.errors import ErrorResponse
from app.services.auth_service import auth_service


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    return auth_service.register(db, payload)


@router.post("/signup", response_model=AuthResponse, status_code=201, include_in_schema=False)
def signup_alias(
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    return auth_service.register(db, payload)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    return auth_service.authenticate(db, payload)


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(require_active_user)]) -> UserResponse:
    return auth_service.to_user_response(current_user)


@router.post("/logout", response_model=SuccessResponse)
def logout() -> SuccessResponse:
    return SuccessResponse(success=True)


@router.post("/recover-password", response_model=SuccessResponse)
def recover_password(_: RecoverPasswordRequest) -> SuccessResponse:
    return SuccessResponse(
        success=True,
        message="If an account exists for this email, a recovery code will be sent.",
    )