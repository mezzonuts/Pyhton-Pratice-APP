from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.app.database import Base
from backend.app.models.mission import MissionTemplate, MissionMode
from enum import Enum


class MissionStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"
    FAILED = "failed"


class MissionGrade(Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    F = "F"


class UserMissionState(Base):
    __tablename__ = "user_mission_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mission_id = Column(Integer, ForeignKey("mission_templates.id"), nullable=False)
    mission_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(MissionStatus), nullable=False, default=MissionStatus.NOT_STARTED)
    grade = Column(Enum(MissionGrade), nullable=True)
    score = Column(Integer, nullable=True)
    xp_earned = Column(Integer, nullable=False, default=0)
    elo_change = Column(Integer, nullable=True)
    code_snapshot = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "mission_date", name="unique_user_mission_constraint"
        ),
    ),