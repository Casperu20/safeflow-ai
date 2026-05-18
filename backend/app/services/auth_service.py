from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.schemas.errors import ApiError


password_hasher = PasswordHash.recommended()


class AuthService:
    def register(self, db: Session, payload: RegisterRequest) -> AuthResponse:
        if self._get_user_by_email(db, payload.email) is not None:
            raise ApiError(
                status_code=409,
                error_code="EMAIL_ALREADY_EXISTS",
                message="An account with this email already exists.",
                details={"email": ["Try logging in instead."]},
            )

        user = User(
            email=payload.email,
            password_hash=self.hash_password(payload.password),
            full_name=payload.fullName,
            role="user",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return self.build_auth_response(user)

    def authenticate(self, db: Session, payload: LoginRequest) -> AuthResponse:
        user = self._get_user_by_email(db, payload.email)

        if user is None or not self.verify_password(payload.password, user.password_hash):
            raise ApiError(
                status_code=401,
                error_code="INVALID_CREDENTIALS",
                message="Invalid email or password.",
                details={},
            )

        if not user.is_active:
            raise ApiError(
                status_code=403,
                error_code="FORBIDDEN",
                message="This account is inactive.",
                details={},
            )

        return self.build_auth_response(user)

    def get_user_from_token(self, db: Session, token: str) -> User:
        self._ensure_auth_is_configured()

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except ExpiredSignatureError as exc:
            raise ApiError(
                status_code=401,
                error_code="TOKEN_EXPIRED",
                message="Authentication token has expired.",
                details={},
            ) from exc
        except InvalidTokenError as exc:
            raise ApiError(
                status_code=401,
                error_code="INVALID_TOKEN",
                message="Invalid authentication token.",
                details={},
            ) from exc

        user_id = payload.get("sub")
        if not isinstance(user_id, str) or not user_id:
            raise ApiError(
                status_code=401,
                error_code="INVALID_TOKEN",
                message="Invalid authentication token.",
                details={},
            )

        user = db.get(User, user_id)
        if user is None:
            raise ApiError(
                status_code=404,
                error_code="USER_NOT_FOUND",
                message="User account was not found.",
                details={},
            )

        return user

    def build_auth_response(self, user: User) -> AuthResponse:
        access_token = self.create_access_token(user)
        return AuthResponse(user=self.to_user_response(user), accessToken=access_token)

    def to_user_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            fullName=user.full_name,
            role=user.role,
            createdAt=user.created_at,
        )

    def create_access_token(self, user: User) -> str:
        self._ensure_auth_is_configured()

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )
        payload = {
            "sub": user.id,
            "type": "access",
            "exp": expires_at,
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def hash_password(self, password: str) -> str:
        return password_hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hasher.verify(password, password_hash)

    def _get_user_by_email(self, db: Session, email: str | None) -> User | None:
        if not email:
            return None

        return db.scalar(select(User).where(User.email == email))

    def _ensure_auth_is_configured(self) -> None:
        if settings.jwt_secret_key:
            return

        raise ApiError(
            status_code=500,
            error_code="SERVER_ERROR",
            message="Authentication is not configured on the backend.",
            details={
                "auth": [
                    "Set JWT_SECRET_KEY in backend/.env or in the process environment and restart the backend."
                ]
            },
        )


auth_service = AuthService()