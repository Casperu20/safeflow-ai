from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.errors import ApiError
from app.services.auth_service import auth_service


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    token = _extract_bearer_token(credentials)
    if token is None:
        raise ApiError(
            status_code=401,
            error_code="UNAUTHORIZED",
            message="Authentication is required.",
            details={},
        )

    return auth_service.get_user_from_token(db, token)


def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    token = _extract_bearer_token(credentials)
    if token is None:
        return None

    user = auth_service.get_user_from_token(db, token)
    if user.is_active:
        return user

    raise ApiError(
        status_code=403,
        error_code="FORBIDDEN",
        message="This account is inactive.",
        details={},
    )


def require_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.is_active:
        return current_user

    raise ApiError(
        status_code=403,
        error_code="FORBIDDEN",
        message="This account is inactive.",
        details={},
    )


def _extract_bearer_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    if credentials is None:
        return None

    if credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise ApiError(
            status_code=401,
            error_code="INVALID_TOKEN",
            message="Invalid authentication token.",
            details={},
        )

    return credentials.credentials