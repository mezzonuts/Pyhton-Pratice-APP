from datetime import date, datetime, timedelta
from random import Random
from typing import List, Optional, Set

from app.database import AsyncSessionLocal
from app.models.mission import MissionMode, MissionTemplate
from app.models.user_mission import (
    MissionStatus,
    MissionGrade,
    UserMissionState,
)
from sqlalchemy import select, and_


MODE_WEIGHTS = {
    0: {
        MissionMode.FIX_BUG: 0.50,
        MissionMode.BUILD_FEATURE: 0.30,
        MissionMode.REFACTOR: 0.20,
    },
    1: {
        MissionMode.FIX_BUG: 0.35,
        MissionMode.BUILD_FEATURE: 0.45,
        MissionMode.REFACTOR: 0.20,
    },
    2: {
        MissionMode.FIX_BUG: 0.25,
        MissionMode.BUILD_FEATURE: 0.40,
        MissionMode.REFACTOR: 0.35,
    },
    3: {
        MissionMode.FIX_BUG: 0.20,
        MissionMode.BUILD_FEATURE: 0.50,
        MissionMode.REFACTOR: 0.30,
    },
    4: {
        MissionMode.FIX_BUG: 0.15,
        MissionMode.BUILD_FEATURE: 0.40,
        MissionMode.REFACTOR: 0.45,
    },
}

TIER1_DIFFICULTY_RANGE = (1100, 1250)

TIER_TAGS = {
    0: {"basic", "logic", "string", "loop", "function"},
    1: {"data_wrangling", "json", "csv", "error_handling", "big_o"},
    2: {"oop", "patterns", "typing", "testing", "logging", "pep8"},
    3: {"api", "async", "etl", "concurrency", "optimization"},
    4: {"refactoring", "debugging", "security", "architecture", "legacy"},
}


def _get_unlocked_tags(tier: int) -> Set[str]:
    unlocked: Set[str] = set()
    for t in range(tier + 1):
        unlocked.update(TIER_TAGS.get(t, set()))
    return unlocked


class DailyMissionGenerator:
    def __init__(self, mission_repo=None):
        self.mission_repo = mission_repo

    def generate_daily_mission(
        self, user_state: UserMissionState, target_date: date
    ) -> Optional[MissionTemplate]:
        available = self._get_available_missions(user_state, target_date)
        if not available:
            return None

        mode = self._select_mode(user_state.tier)

        # Tier 1: add skill-targeted missions
        if user_state.tier >= 1 or user_state.elo_rating >= 1100:
            skill_missions = self._select_skill_targeted_missions(user_state)
            available = available + skill_missions

        mode_missions = [m for m in available if m.mode == mode]
        if not mode_missions:
            import random as _random

            mode_missions = available
            mode = _random.choices(
                list(MissionMode),
                weights=[0.50, 0.30, 0.20],
                k=1,
            )[0]

        scored = self._score_by_difficulty(mode_missions, user_state.elo_rating)
        top_candidates = scored[:5]
        selected = self._weighted_random_select(
            top_candidates, user_state, target_date
        )
        return selected

    def _select_skill_targeted_missions(self, user_state: UserMissionState) -> List[MissionTemplate]:
        """Recommend missions based on weakest 2 skill dimensions from skill_radar."""
        skill_radar = user_state.skill_radar or {}
        if not skill_radar:
            return []

        # Sort skills by proficiency (ascending - weakest first)
        sorted_skills = sorted(skill_radar.items(), key=lambda x: x[1])
        weakest_2 = sorted_skills[:2]

        # Map weakest skill tags to difficulty_types
        tag_to_difficulty = {
            "json": "data_wrangling",
            "csv": "data_wrangling",
            "error_handling": "error_handling",
            "big_o": "big_o",
        }

        selected = []
        for skill_name, proficiency in weakest_2:
            difficulty_type = tag_to_difficulty.get(skill_name, "data_wrangling")
            # Get missions from repo matching this difficulty type and Tier 1
            if self.mission_repo:
                missions = self.mission_repo.get_by_difficulty_type(
                    difficulty_type, tier=1
                )
            else:
                from app.services.mission_seed import mission_repo as sr
                missions = sr.get_by_difficulty_type(difficulty_type, tier=1)

            filtered = [
                m
                for m in missions
                if m.difficulty_rating in range(1100, 1251)
                and m.prerequisite_tier == 0
            ]
            selected.extend(filtered)

        # Deduplicate and limit to 4
        seen = set()
        unique = []
        for m in selected:
            if m.id not in seen:
                seen.add(m.id)
                unique.append(m)
        return unique[:4]

    def _get_all_missions(self) -> List[MissionTemplate]:
        if self.mission_repo:
            return self.mission_repo.get_all_missions()
        from app.services.mission_seed import mission_repo as sr
        return sr.get_all_missions()

    async def _get_available_missions(
        self, user_state: UserMissionState, target_date: date
    ) -> List[MissionTemplate]:
        if self.mission_repo:
            all_missions = self.mission_repo.get_by_tier(user_state.tier)
        else:
            from app.services.mission_seed import mission_repo as sr
            all_missions = sr.get_by_tier(user_state.tier)

        # Filter: include Tier 1 missions when user.tier >= 1 OR user.elo_rating >= 1100
        tier_threshold = user_state.tier if user_state.tier >= 1 else 0
        filtered = [
            m
            for m in all_missions
            if not (m.tier == 1 and user_state.tier < 1 and user_state.elo_rating < 1100)
        ]

        # Get recently completed mission IDs from the user's mission history
        cutoff_date = date.today() - timedelta(days=30)

        recent_completed: Set[int] = set()
        if user_state.user_id is not None:
            try:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(
                        select(UserMissionState.mission_id, UserMissionState.completed_at)
                        .where(
                            and_(
                                UserMissionState.user_id == user_state.user_id,
                                UserMissionState.status == MissionStatus.GRADED,
                            )
                        )
                    )
                    rows = result.all()
                    for mission_id, completed_at in rows:
                        if completed_at and completed_at > cutoff_date:
                            recent_completed.add(mission_id)
            except Exception:
                pass  # If DB not available, skip this filter

        unlocked_tags = _get_unlocked_tags(user_state.tier)

        return [
            m
            for m in all_missions
            if m.id not in recent_completed
            and all(tag in unlocked_tags for tag in m.tags)
        ]

    def _select_mode(self, tier: int) -> MissionMode:
        weights = MODE_WEIGHTS[tier]
        modes = list(weights.keys())
        probabilities = list(weights.values())
        return choices(modes, weights=probabilities, k=1)[0]

    def _score_by_difficulty(
        self, missions: List[MissionTemplate], user_elo: int
    ) -> List[MissionTemplate]:
        import math

        def difficulty_score(mission: MissionTemplate) -> float:
            # Tier 1 difficulty range is 1100-1250
            tier_difficulty_range = TIER1_DIFFICULTY_RANGE
            if mission.tier == 1 and tier_difficulty_range[0] <= mission.difficulty_rating <= tier_difficulty_range[1]:
                # Clamp penalty to Tier 1 range
                effective_elo = max(tier_difficulty_range[0], min(tier_difficulty_range[1], user_elo))
            else:
                effective_elo = user_elo
            diff = abs(effective_elo - mission.difficulty_rating)
            return math.exp(-(diff ** 2) / (2 * 100 ** 2))

        return sorted(missions, key=difficulty_score, reverse=True)

    def _weighted_random_select(
        self,
        candidates: List[MissionTemplate],
        user_state: UserMissionState,
        target_date: date,
    ) -> MissionTemplate:
        seed = int(
            hash(f"{user_state.user_id}{target_date.isoformat()}") % (2**31)
        )
        rng = Random(seed)

        if not candidates:
            from app.models.mission import MissionTemplate as MT

            return MT(id=0, tier=0, mode=MissionMode.FIX_BUG)

        weights = [1.0 / (i + 1) for i in range(len(candidates))]
        return choices(candidates, weights=weights, k=1)[0]


mission_service = DailyMissionGenerator()