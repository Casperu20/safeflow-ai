from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.analysis_history import AnalysisHistory
from app.models.user import User
from app.schemas.errors import ApiError
from app.schemas.history import AnalysisHistoryItemResponse, AnalysisHistoryListResponse
from app.schemas.scam_analysis import EvidenceItem, ScamAnalysisResponse
from app.services.extraction.extraction_models import AnalysisSubmission, ExtractionResult
from app.utils.text_sanitization import redact_sensitive_text, safe_text_excerpt


class HistoryService:
    def create_history_record(
        self,
        db: Session,
        *,
        user: User,
        submission: AnalysisSubmission,
        extraction: ExtractionResult,
        analysis_response: ScamAnalysisResponse,
    ) -> AnalysisHistory:
        analysis_id = analysis_response.analysisId
        if not analysis_id:
            raise ApiError(
                status_code=500,
                error_code="SERVER_ERROR",
                message="Analysis identifier is missing from the response.",
                details={},
            )

        record = AnalysisHistory(
            id=analysis_id,
            user_id=user.id,
            input_type=extraction.input_type,
            original_filename=submission.file.filename if submission.file is not None else None,
            input_preview=safe_text_excerpt(extraction.normalized_text, max_length=160),
            risk_score=analysis_response.riskScore,
            risk_level=analysis_response.riskLevel,
            detected_scam_type=analysis_response.detectedScamType,
            explanation=redact_sensitive_text(analysis_response.explanation),
            indicators=list(analysis_response.indicators or []),
            recommendation=redact_sensitive_text(analysis_response.recommendation),
            evidence=[
                self._serialize_evidence_item(item)
                for item in analysis_response.evidence or []
            ],
            extraction_method=extraction.extraction_method,
            analysis_mode=analysis_response.analysisMode,
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_history(
        self,
        db: Session,
        *,
        user: User,
        limit: int,
        offset: int,
        risk_level: str | None,
        input_type: str | None,
    ) -> AnalysisHistoryListResponse:
        filters = [AnalysisHistory.user_id == user.id]
        if risk_level:
            filters.append(AnalysisHistory.risk_level == risk_level)
        if input_type:
            filters.append(AnalysisHistory.input_type == input_type)

        total = db.scalar(
            select(func.count()).select_from(AnalysisHistory).where(*filters),
        ) or 0

        items = db.scalars(
            select(AnalysisHistory)
            .where(*filters)
            .order_by(AnalysisHistory.created_at.desc())
            .offset(offset)
            .limit(limit),
        ).all()

        return AnalysisHistoryListResponse(
            items=[self.to_response_model(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_history_item(self, db: Session, *, user: User, analysis_id: str) -> AnalysisHistory:
        item = db.scalar(
            select(AnalysisHistory).where(
                AnalysisHistory.id == analysis_id,
                AnalysisHistory.user_id == user.id,
            ),
        )
        if item is None:
            raise ApiError(
                status_code=404,
                error_code="HISTORY_ITEM_NOT_FOUND",
                message="History item was not found.",
                details={},
            )

        return item

    def delete_history_item(self, db: Session, *, user: User, analysis_id: str) -> None:
        item = self.get_history_item(db, user=user, analysis_id=analysis_id)
        db.delete(item)
        db.commit()

    def to_response_model(self, item: AnalysisHistory) -> AnalysisHistoryItemResponse:
        evidence = [EvidenceItem.model_validate(raw_item) for raw_item in item.evidence or []]
        return AnalysisHistoryItemResponse(
            analysisId=item.id,
            inputType=item.input_type,
            originalFilename=item.original_filename,
            inputPreview=item.input_preview,
            riskScore=item.risk_score,
            riskLevel=item.risk_level,
            detectedScamType=item.detected_scam_type,
            explanation=item.explanation,
            indicators=list(item.indicators or []),
            recommendation=item.recommendation,
            evidence=evidence,
            extractionMethod=item.extraction_method,
            analysisMode=item.analysis_mode,
            createdAt=item.created_at,
        )

    def _serialize_evidence_item(self, item: EvidenceItem) -> dict[str, object]:
        return {
            "text": redact_sensitive_text(item.text),
            "reason": item.reason,
            "severity": item.severity,
        }


history_service = HistoryService()