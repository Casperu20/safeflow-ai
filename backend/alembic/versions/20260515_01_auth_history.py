"""Add users and analysis history tables.

Revision ID: 20260515_01
Revises:
Create Date: 2026-05-15 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260515_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "analysis_history",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("input_type", sa.String(length=16), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("input_preview", sa.Text(), nullable=True),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("detected_scam_type", sa.String(length=255), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("indicators", sa.JSON(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("extraction_method", sa.String(length=32), nullable=True),
        sa.Column("analysis_mode", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_history_created_at"), "analysis_history", ["created_at"], unique=False)
    op.create_index(op.f("ix_analysis_history_input_type"), "analysis_history", ["input_type"], unique=False)
    op.create_index(op.f("ix_analysis_history_risk_level"), "analysis_history", ["risk_level"], unique=False)
    op.create_index(op.f("ix_analysis_history_user_id"), "analysis_history", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_analysis_history_user_id"), table_name="analysis_history")
    op.drop_index(op.f("ix_analysis_history_risk_level"), table_name="analysis_history")
    op.drop_index(op.f("ix_analysis_history_input_type"), table_name="analysis_history")
    op.drop_index(op.f("ix_analysis_history_created_at"), table_name="analysis_history")
    op.drop_table("analysis_history")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")