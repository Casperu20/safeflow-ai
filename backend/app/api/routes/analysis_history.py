from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import SuccessResponse
from app.schemas.errors import ErrorResponse
from app.schemas.history import AnalysisHistoryItemResponse, AnalysisHistoryListResponse
from app.schemas.scam_analysis import InputType, RiskLevel
from app.services.history_service import history_service


router = APIRouter(
    prefix="/api/analysis-history",
    tags=["analysis-history"],
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)


@router.get("", response_model=AnalysisHistoryListResponse)
def get_analysis_history(
    current_user: Annotated[User, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    riskLevel: RiskLevel | None = Query(default=None),
    inputType: InputType | None = Query(default=None),
) -> AnalysisHistoryListResponse:
    return history_service.list_history(
        db,
        user=current_user,
        limit=limit,
        offset=offset,
        risk_level=riskLevel,
        input_type=inputType,
    )


@router.get("/{analysis_id}", response_model=AnalysisHistoryItemResponse)
def get_analysis_history_item(
    analysis_id: str,
    current_user: Annotated[User, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AnalysisHistoryItemResponse:
    item = history_service.get_history_item(db, user=current_user, analysis_id=analysis_id)
    return history_service.to_response_model(item)


@router.delete("/{analysis_id}", response_model=SuccessResponse)
def delete_analysis_history_item(
    analysis_id: str,
    current_user: Annotated[User, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SuccessResponse:
    history_service.delete_history_item(db, user=current_user, analysis_id=analysis_id)
    return SuccessResponse(success=True)