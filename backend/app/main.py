from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.analysis_history import router as analysis_history_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.scam_analysis import router as scam_analysis_router
from app.core.config import settings
from app.schemas.errors import ApiError, ErrorResponse


LOCAL_FRONTEND_ORIGINS = [
    settings.frontend_origin,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def create_app() -> FastAPI:
    if settings.is_production and not settings.jwt_secret_key:
        raise RuntimeError("JWT_SECRET_KEY is required in production.")

    app = FastAPI(title="SafeFlow AI Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(dict.fromkeys(LOCAL_FRONTEND_ORIGINS)),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(analysis_history_router)
    app.include_router(health_router)
    app.include_router(scam_analysis_router)

    @app.exception_handler(ApiError)
    async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_response().model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        details: dict[str, list[str]] = {}

        for error in exc.errors():
            field = str(error.get("loc", ["body"])[-1])
            details.setdefault(field, []).append(error.get("msg", "Invalid value."))

        payload = ErrorResponse(
            errorCode="INVALID_REQUEST",
            message="Request validation failed.",
            details=details,
        )

        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, __: Exception) -> JSONResponse:
        payload = ErrorResponse(
            errorCode="SERVER_ERROR",
            message="An unexpected server error occurred.",
            details={},
        )

        return JSONResponse(status_code=500, content=payload.model_dump())

    return app


app = create_app()