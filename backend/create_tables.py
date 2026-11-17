import os, sys
sys.path.insert(0, r'D:\Project\Pyhton Pratice APP\backend')
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean, JSON, Enum, ForeignKey, Text, UniqueConstraint

engine = create_engine("sqlite:///./test.db")
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("email", String, unique=True, index=True, nullable=False),
    Column("username", String, unique=True, index=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("tier", Integer, default=0),
    Column("elo_rating", Integer, default=1000),
    Column("streak_days", Integer, default=0),
    Column("longest_streak", Integer, default=0),
    Column("freeze_shields", Integer, default=0),
    Column("total_xp", Integer, default=0),
    Column("skill_radar", JSON, default={}),
    Column("ai_config", JSON, default={}),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), server_default="now()"),
    Column("last_active", DateTime(timezone=True), server_default="now()"),
)

mission_templates = Table(
    "mission_templates",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, nullable=False),
    Column("tier", Integer, nullable=False),
    Column(
        "mode",
        Enum("fix_bug", "build_feature", "refactor", name="missionmode", native_enum=False),
        nullable=False,
    ),
    Column("ticket_markdown", Text, nullable=False),
    Column("starter_code", Text, nullable=False),
    Column("solution_code", Text, nullable=False),
    Column("test_file", Text, nullable=False),
    Column("expected_interface", Text, nullable=False),
    Column("time_limit_minutes", Integer, nullable=False),
    Column("xp_reward", Integer, nullable=False),
    Column("difficulty_rating", Integer, nullable=False),
    Column("tags", JSON, nullable=False, default=[]),
    Column("is_boss_fight", Boolean, nullable=False, default=False),
    Column("created_at", DateTime(timezone=True), server_default="now()"),
)

user_mission_states = Table(
    "user_mission_states",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("mission_id", Integer, ForeignKey("mission_templates.id"), nullable=False),
    Column("mission_date", DateTime(timezone=True), nullable=False),
    Column(
        "status",
        Enum("not_started", "in_progress", "submitted", "graded", "failed", name="missionstatus", native_enum=False),
        nullable=False,
    ),
    Column(
        "grade",
        Enum("S", "A", "B", "C", "F", name="missiongrade", native_enum=False),
        nullable=True,
    ),
    Column("score", Integer, nullable=True),
    Column("xp_earned", Integer, nullable=False, default=0),
    Column("elo_change", Integer, nullable=True),
    Column("code_snapshot", Text, nullable=True),
    Column("started_at", DateTime(timezone=True), nullable=True),
    Column("submitted_at", DateTime(timezone=True), nullable=True),
    Column("completed_at", DateTime(timezone=True), nullable=True),
    __table_args__ = (
        UniqueConstraint("user_id", "mission_date", name="unique_user_mission_constraint"),
    ),
)

metadata.create_all(engine)
print("Tables created successfully!")