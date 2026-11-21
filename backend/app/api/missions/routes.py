from fastapi import APIRouter, Depends, HTTPException, status
from random import Random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.mission import MissionTemplate, MissionMode
from app.models.user_mission import (
    UserMissionState,
    MissionStatus,
    MissionGrade,
)
from app.services.mission_service import (
    DailyMissionGenerator,
    _get_unlocked_tags,
)
from app.schemas.user import UserRead

router = APIRouter(prefix="/v1/missions", tags=["missions"])

mission_service = DailyMissionGenerator()


get_async_session = AsyncSessionLocal


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
) -> User:
    result = await session.execute(select(User).where(User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/daily", response_model=dict)
async def get_daily_mission(
    user: User = Depends(get_current_user),
):
    from datetime import date
    target_date = date.today()
    user_state = UserMissionState(
        user_id=user.id,
        mission_date=datetime.now(),
        status="not_started",
    )
    mission = mission_service.generate_daily_mission(user_state, target_date)
    if not mission:
        raise HTTPException(
            status_code=404, detail="No daily mission available"
        )
    return {
        "mission_id": mission.id,
        "title": mission.title,
        "mode": mission.mode.value,
        "tier": mission.tier,
        "ticket_markdown": mission.ticket_markdown,
        "starter_code": mission.starter_code,
        "test_file": mission.test_file,
        "expected_interface": mission.expected_interface,
        "time_limit_minutes": mission.time_limit_minutes,
        "xp_reward": mission.xp_reward,
        "difficulty_rating": mission.difficulty_rating,
        "tags": mission.tags,
        "is_boss_fight": mission.is_boss_fight,
    }


@router.get("/tier1", response_model=dict)
async def get_tier1_missions(
    user: User = Depends(get_current_user),
):
    """Return 4 randomly selected Tier 1 missions appropriate for user's ELO."""
    # Tier 1 missions available when user.tier >= 1 OR user.elo_rating >= 1100
    if user.tier < 1 and user.elo_rating < 1100:
        raise HTTPException(
            status_code=404, detail="Tier 1 missions not unlocked yet"
        )

    # Get Tier 1 missions from repo
    if mission_service.mission_repo:
        all_missions = mission_service.mission_repo.get_by_tier(1)
    else:
        from app.services.mission_seed import mission_repo as sr
        all_missions = sr.get_by_tier(1)

    # Filter for elo-appropriate missions
    appropriate = [
        m
        for m in all_missions
        if m.difficulty_rating in range(1100, 1251)
        and (user.tier >= 1 or user.elo_rating >= 1100)
    ]

    if not appropriate:
        raise HTTPException(
            status_code=404, detail="No Tier 1 missions available for your ELO"
        )

    # Deterministic selection: seed = hash(user_id + target_date)
    from datetime import date
    target_date = date.today()
    seed = int(
        hash(f"{user.id}{target_date.isoformat()}") % (2**31)
    )
    rng = Random(seed)
    selected = rng.sample(appropriate, min(4, len(appropriate)))

    return {
        "missions": [
            {
                "mission_id": m.id,
                "title": m.title,
                "mode": m.mode.value,
                "tier": m.tier,
                "difficulty_rating": m.difficulty_rating,
                "difficulty_type": m.difficulty_type,
                "starter_code": m.starter_code,
                "test_file": m.test_file,
            }
            for m in selected
        ]
    }


@router.get("/history", response_model=dict)
async def get_mission_history(
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(UserMissionState)
        .where(UserMissionState.user_id == user.id)
        .order_by(UserMissionState.mission_date.desc())
        .offset(skip)
        .limit(limit)
    )
    missions = result.scalars().all()
    return {
        "history": [
            {
                "id": m.id,
                "mission_date": m.mission_date,
                "status": m.status.value,
                "grade": m.grade.value if m.grade else None,
                "score": m.score,
                "xp_earned": m.xp_earned,
                "elo_change": m.elo_change,
                "mission": {
                    "id": m.mission.id,
                    "title": m.mission.title,
                    "mode": m.mission.mode.value,
                    "tier": m.mission.tier,
                },
            }
            for m in missions
        ]
    }


@router.post("/daily/start", response_model=dict)
async def start_daily_mission(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    target_date = datetime.utcnow().date()
    existing = await session.execute(
        select(UserMissionState).where(
            UserMissionState.user_id == user.id,
            UserMissionState.mission_date >= datetime(
                target_date.year, target_date.month, target_date.day
            ),
        )
    )
    user_mission = existing.scalar_one_or_none()

    if not user_mission:
        user_mission = UserMissionState(
            user_id=user.id,
            mission_id=0,
            mission_date=datetime.now(),
            status=MissionStatus.IN_PROGRESS,
        )
        session.add(user_mission)
        await session.commit()
        await session.refresh(user_mission)
    else:
        user_mission.status = MissionStatus.IN_PROGRESS
        user_mission.started_at = datetime.utcnow()
        await session.commit()

    return {
        "id": user_mission.id,
        "status": user_mission.status.value,
        "started_at": user_mission.started_at,
    }


@router.post("/daily/submit", response_model=dict)
async def submit_daily_mission(
    code: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Find the active user mission
    result = await session.execute(
        select(UserMissionState).where(
            UserMissionState.user_id == user.id,
            UserMissionState.status == MissionStatus.IN_PROGRESS,
        )
    )
    user_mission = result.scalar_one_or_none()

    if not user_mission:
        raise HTTPException(
            status_code=400, detail="No active mission to submit"
        )

    user_mission.status = MissionStatus.SUBMITTED
    user_mission.submitted_at = datetime.utcnow()
    user_mission.code_snapshot = code
    await session.commit()

    return {
        "id": user_mission.id,
        "status": user_mission.status.value,
        "submitted_at": user_mission.submitted_at,
        "message": "Mission submitted for grading",
    }


@router.get("/progression", response_model=dict)
async def check_tier_progression(
    user: User = Depends(get_current_user),
):
    elo = user.elo_rating
    tier = user.tier

    tier_thresholds = {
        0: 0,
        1: 1100,
        2: 1250,
        3: 1400,
        4: 1600,
    }

    unlocked_next = False
    next_tier = tier + 1
    if next_tier <= 4 and elo >= tier_thresholds[next_tier]:
        unlocked_next = True

    # Calculate missions needed
    missions_needed = {
        0: 0,
        1: 10,
        2: 25,
        3: 50,
        4: 100,
    }

    # Skill target display
    skill_radar = user.skill_radar or {}
    skill_target_display = {}
    if skill_radar:
        sorted_skills = sorted(skill_radar.items(), key=lambda x: x[1])
        weakest_2 = sorted_skills[:2]
        skill_target_display = {
            skill: proficiency
            for skill, proficiency in weakest_2
        }

    return {
        "current_tier": tier,
        "current_elo": elo,
        "next_tier_threshold": tier_thresholds.get(next_tier, None)
        if next_tier <= 4
        else None,
        "unlocked_next": unlocked_next,
        "missions_for_next_tier": missions_needed.get(next_tier, 0),
        "missions_completed": user_mission.completed_mission_ids
        if hasattr(user_mission, "completed_mission_ids")
        else 0,
        "skill_target_display": skill_target_display,
    }