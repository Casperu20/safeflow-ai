from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    input_type: Mapped[str] = mapped_column(String(16), index=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(16), index=True)
    detected_scam_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    explanation: Mapped[str] = mapped_column(Text)
    indicators: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    extraction_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    analysis_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)

    user = relationship("User", back_populates="analyses")