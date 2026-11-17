from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    tier = Column(Integer, default=0)
    elo_rating = Column(Integer, default=1000)
    streak_days = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    freeze_shields = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    skill_radar = Column(JSON, default={})
    ai_config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )