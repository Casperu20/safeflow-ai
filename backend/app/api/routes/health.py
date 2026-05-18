from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@router.get("/api/health")
async def api_health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}