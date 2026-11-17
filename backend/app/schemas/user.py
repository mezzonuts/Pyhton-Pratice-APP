from typing import Optional, Literal
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    email: str
    username: str
    tier: int = 0
    elo_rating: int = 1000
    streak_days: int = 0
    longest_streak: int = 0
    freeze_shields: int = 0
    total_xp: int = 0
    skill_radar: dict = {}
    ai_config: dict = {}
    is_active: bool
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True