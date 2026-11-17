"""Create mission_tables

Revision ID: 20261117_001
Revises: None
Create Date: 2026-11-17 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = "20261117_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mission_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column(
            "mode",
            sa.Enum(
                "fix_bug",
                "build_feature",
                "refactor",
                name="missionmode",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("ticket_markdown", sa.Text(), nullable=False),
        sa.Column("starter_code", sa.Text(), nullable=False),
        sa.Column("solution_code", sa.Text(), nullable=False),
        sa.Column("test_file", sa.Text(), nullable=False),
        sa.Column("expected_interface", sa.Text(), nullable=False),
        sa.Column("time_limit_minutes", sa.Integer(), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False),
        sa.Column("difficulty_rating", sa.Integer(), nullable=False),
        sa.Column("tags", JSON(), nullable=False, default=[]),
        sa.Column(
            "is_boss_fight",
            sa.Boolean(),
            nullable=False,
            default=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_mission_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("mission_id", sa.Integer(), nullable=False),
        sa.Column("mission_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "not_started",
                "in_progress",
                "submitted",
                "graded",
                "failed",
                name="missionstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "grade",
            sa.Enum(
                "S",
                "A",
                "B",
                "C",
                "F",
                name="missiongrade",
                native_enum=False,
            ),
            nullable=True,
        ),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("xp_earned", sa.Integer(), nullable=False, default=0),
        sa.Column("elo_change", sa.Integer(), nullable=True),
        sa.Column("code_snapshot", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "mission_date", name="unique_user_mission_constraint"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_mission_states")
    op.drop_table("mission_templates")