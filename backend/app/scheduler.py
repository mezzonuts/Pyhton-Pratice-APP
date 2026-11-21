import asyncio
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.mission import MissionTemplate, MissionMode
from app.models.user_mission import UserMissionState, MissionStatus, MissionGrade
from app.services.mission_service import DailyMissionGenerator, _get_unlocked_tags

from sqlalchemy import select, func, and_, or_


mission_service = DailyMissionGenerator()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def generate_daily_missions_for_all_users():
    """Generate daily missions for all active users at 00:00 WIB."""
    print(f"[{datetime.now()}] Starting daily mission generation...")

    async with AsyncSessionLocal() as session:
        # Get all active users
        result = await session.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()

        for user in users:
            try:
                await generate_daily_mission_for_user(session, user)
            except Exception as e:
                print(f"Error generating mission for user {user.id}: {e}")

        await session.commit()
    print(f"[{datetime.now()}] Daily mission generation completed.")


async def generate_daily_mission_for_user(session, user):
    """Generate daily mission for a single user."""
    target_date = datetime.now(ZoneInfo("Asia/Dhaka")).date()
    wib = ZoneInfo("Asia/Dhaka")

    # Check if user already has a mission for today
    result = await session.execute(
        select(UserMissionState).where(
            UserMissionState.user_id == user.id,
            func.date(UserMissionState.mission_date) == target_date,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Check if the existing mission is for the same date and still not completed
        if existing.status in (MissionStatus.NOT_STARTED, MissionStatus.IN_PROGRESS):
            return  # Already has a mission for today
        elif existing.status == MissionStatus.SUBMITTED:
            # Generate new mission if submitted
            existing.status = MissionStatus.NOT_STARTED
            existing.started_at = None
            existing.submitted_at = None
            existing.completed_at = None
        else:
            return

    # Get user's current tier and unlocked tags
    tier = user.tier
    unlocked_tags = _get_unlocked_tags(tier)

    # Get available missions for this tier
    result = await session.execute(
        select(MissionTemplate).where(MissionTemplate.tier == tier)
    )
    all_missions = result.scalars().all()

    # Filter out recently completed missions (last 30 days)
    cutoff_date = datetime.now() - timedelta(days=30)
    completed_ids = set()
    # Get user's completed mission IDs from user_mission_states
    result2 = await session.execute(
        select(UserMissionState.mission_id).where(
            and_(
                UserMissionState.user_id == user.id,
                UserMissionState.status == MissionStatus.GRADED,
            )
        )
    )
    completed_rows = result2.scalars().all()
    for mid in completed_rows:
        # Get the completion date
        result3 = await session.execute(
            select(UserMissionState.completed_at).where(
                UserMissionState.id == mid
            )
        )
        row = result3.scalar_one_or_none()
        if row and row > cutoff_date:
            completed_ids.add(mid)

    # Filter available missions
    available = [
        m
        for m in all_missions
        if m.id not in completed_ids
        and all(tag in unlocked_tags for tag in m.tags)
    ]

    if not available:
        print(f"User {user.id} (tier {tier}): no available missions")
        return

    # Select mode based on tier weights
    weights = {
        0: {MissionMode.FIX_BUG: 0.50, MissionMode.BUILD_FEATURE: 0.30, MissionMode.REFACTOR: 0.20},
        1: {MissionMode.FIX_BUG: 0.35, MissionMode.BUILD_FEATURE: 0.45, MissionMode.REFACTOR: 0.20},
        2: {MissionMode.FIX_BUG: 0.25, MissionMode.BUILD_FEATURE: 0.40, MissionMode.REFACTOR: 0.35},
        3: {MissionMode.FIX_BUG: 0.20, MissionMode.BUILD_FEATURE: 0.50, MissionMode.REFACTOR: 0.30},
        4: {MissionMode.FIX_BUG: 0.15, MissionMode.BUILD_FEATURE: 0.40, MissionMode.REFACTOR: 0.45},
    }

    import random
    modes = list(weights[tier].keys())
    probabilities = list(weights[tier].values())
    mode = random.choices(modes, weights=probabilities, k=1)[0]

    # Filter missions by selected mode
    mode_missions = [m for m in available if m.mode == mode]
    if not mode_missions:
        mode_missions = available
        mode = random.choice(modes)

    # Score by difficulty
    import math

    def difficulty_score(mission):
        diff = abs(mission.difficulty_rating - user.elo_rating)
        return math.exp(-(diff ** 2) / (2 * 100 ** 2))

    scored = sorted(mode_missions, key=difficulty_score, reverse=True)
    top_candidates = scored[:5]

    # Weighted random select with deterministic seed
    seed = int(hash(f"{user.id}{target_date.isoformat()}") % (2**31))
    rng = random.Random(seed)

    weights_select = [1.0 / (i + 1) for i in range(len(top_candidates))]
    selected = rng.choices(top_candidates, weights=weights_select, k=1)[0]

    # Create user mission state
    new_user_mission = UserMissionState(
        user_id=user.id,
        mission_id=selected.id,
        mission_date=datetime.now(wib),
        status=MissionStatus.NOT_STARTED,
    )

    session.add(new_user_mission)
    await session.commit()

    print(
        f"User {user.id} (tier {tier}, ELO {user.elo_rating}): generated {selected.title} "
        f"(mode: {selected.mode.value}) for {target_date}"
    )


async def start_scheduler():
    """Start the APScheduler to trigger daily at 00:00 WIB."""
    scheduler = AsyncIOScheduler()

    # Trigger at 00:00 WIB (Western Indonesian Time = UTC+7)
    # Cron expression: minute=0, hour=0 (but we need to handle timezone)
    # APScheduler uses the server timezone, so we set the trigger accordingly

    trigger = CronTrigger(
        hour=0, minute=0, timezone=ZoneInfo("Asia/Dhaka")
    )

    scheduler.add_job(
        generate_daily_missions_for_all_users,
        trigger=trigger,
        id="daily_mission_generator",
        replace_existing=True,
    )

    scheduler.start()
    print(
        f"[{datetime.now()}] Scheduler started - daily mission generation at 00:00 WIB"
    )

    # Keep the scheduler running
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(start_scheduler())