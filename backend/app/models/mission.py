from sqlalchemy import (
    String,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Text,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.user import User
from enum import Enum
import json


class MissionMode(Enum):
    FIX_BUG = "fix_bug"
    BUILD_FEATURE = "build_feature"
    REFACTOR = "refactor"


difficulty_type_choices = ["data_wrangling", "error_handling", "big_o"]


class MissionTemplate(Base):
    __tablename__ = "mission_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    tier = Column(Integer, nullable=False)
    mode = Column(Enum(MissionMode), nullable=False)
    difficulty_type = Column(
        String, nullable=False, default="data_wrangling"
    )
    prerequisite_tier = Column(Integer, nullable=False, default=0)
    ticket_markdown = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=False)
    solution_code = Column(Text, nullable=False)
    test_file = Column(Text, nullable=False)
    expected_interface = Column(Text, nullable=False)
    time_limit_minutes = Column(Integer, nullable=False)
    xp_reward = Column(Integer, nullable=False)
    difficulty_rating = Column(Integer, nullable=False)
    tags = Column(JSON, nullable=False, default=list)
    is_boss_fight = Column(Boolean, nullable=False, default=False)
    grading_stage = Column(JSON, nullable=True)
    execution_result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="now()")

    __table_args__ = (
        Index("ix_mission_templates_tier_difficulty", "tier", "difficulty_type"),
        CheckConstraint(
            "difficulty_rating BETWEEN tier * 100 + 100 AND tier * 100 + 150",
            name="ck_mission_difficulty_rating_range",
        ),
    )

    user_mission_states = relationship(
        "UserMissionState", back_populates="mission", cascade="all, delete-orphan"
    )

    @property
    def difficulty_rating_range(self):
        return range(self.tier * 100 + 100, self.tier * 100 + 151)