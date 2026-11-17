# Algorithm Logic Documentation - PyForge
## Core Algorithms & Business Logic Derived from BRD & PRD

---

## 6.1 Overview

This document specifies the core algorithms and business logic that power PyForge's unique value propositions:
1. **Daily Mission Generation** - Adaptive, non-repetitive, skill-targeted
2. **Automated International Grader** - Multi-dimensional code quality assessment
3. **ELO Rating & Skill Radar** - Competency tracking across 5 dimensions
4. **Streak & Gamification Mechanics** - Habit formation with anti-demotivation
5. **AI Provider Routing** - Multi-provider with fallback, cost optimization
6. **Sandbox Security & Resource Management** - Safe code execution
7. **Curriculum Progression & Adaptive Difficulty** - Personalized learning path

---

## 6.2 Daily Mission Generation Algorithm

### 6.2.1 Requirements (from PRD 2.3.1)
- 15-minute daily micro-missions
- 3 modes: Fix the Bug (5m), Build the Feature (10m), Refactor/Code Review (5m)
- Random mode selection weighted by tier
- No repetition within 30 days
- Difficulty matched to user ELO ±100

### 6.2.2 Data Structures

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import random
from datetime import date, timedelta

class MissionMode(Enum):
    FIX_BUG = "fix_bug"
    BUILD_FEATURE = "build_feature"
    REFACTOR = "refactor"

class Tier(int, Enum):
    TIER_0 = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3
    TIER_4 = 4

@dataclass
class MissionTemplate:
    id: str
    tier: Tier
    mode: MissionMode
    title: str
    ticket_markdown: str
    starter_code: str
    solution_code: str
    test_file: str
    expected_interface: str
    time_limit_minutes: int
    xp_reward: int
    difficulty_rating: int  # ELO equivalent
    tags: List[str]
    is_boss_fight: bool = False

@dataclass
class UserMissionState:
    user_id: str
    current_tier: Tier
    elo_rating: int
    completed_mission_ids: set[str]  # Last 30 days
    current_streak: int
    freeze_shields: int
    last_mission_date: Optional[date]
```

### 6.2.3 Mode Weight Configuration

```python
# PRD: "3 mode acak agar tidak monoton" - weighted by tier
MODE_WEIGHTS = {
    Tier.TIER_0: {
        MissionMode.FIX_BUG: 0.50,      # Easier for beginners
        MissionMode.BUILD_FEATURE: 0.30,
        MissionMode.REFACTOR: 0.20,
    },
    Tier.TIER_1: {
        MissionMode.FIX_BUG: 0.35,
        MissionMode.BUILD_FEATURE: 0.45,
        MissionMode.REFACTOR: 0.20,
    },
    Tier.TIER_2: {
        MissionMode.FIX_BUG: 0.25,
        MissionMode.BUILD_FEATURE: 0.40,
        MissionMode.REFACTOR: 0.35,     # More refactor at engineering standards
    },
    Tier.TIER_3: {
        MissionMode.FIX_BUG: 0.20,
        MissionMode.BUILD_FEATURE: 0.50, # Real-job simulation = building
        MissionMode.REFACTOR: 0.30,
    },
    Tier.TIER_4: {
        MissionMode.FIX_BUG: 0.15,
        MissionMode.BUILD_FEATURE: 0.40,
        MissionMode.REFACTOR: 0.45,      # Senior = refactoring focus
    },
}

# Time limits per mode (from PRD)
MODE_TIME_LIMITS = {
    MissionMode.FIX_BUG: 5,
    MissionMode.BUILD_FEATURE: 10,
    MissionMode.REFACTOR: 5,
}
```

### 6.2.4 Core Algorithm: Daily Mission Selection

```python
class DailyMissionGenerator:
    """
    Generates daily mission for a user based on:
    - Current tier & ELO
    - Recent history (avoid repetition)
    - Mode weights for tier
    - Difficulty matching
    """
    
    def __init__(self, mission_repo: MissionRepository):
        self.mission_repo = mission_repo
    
    def generate_daily_mission(
        self, 
        user_state: UserMissionState, 
        target_date: date
    ) -> MissionTemplate:
        """
        Main entry point - returns mission for target_date.
        Deterministic per user per day (seeded by user_id + date).
        """
        # 1. Determine available missions for user's tier
        available = self._get_available_missions(user_state)
        
        if not available:
            # Fallback: generate dynamic mission via AI
            return self._generate_fallback_mission(user_state)
        
        # 2. Select mode based on tier weights
        mode = self._select_mode(user_state.current_tier)
        
        # 3. Filter by selected mode
        mode_missions = [m for m in available if m.mode == mode]
        if not mode_missions:
            # Fallback to any available mode
            mode_missions = available
            mode = random.choice([m.mode for m in available])
        
        # 4. Score missions by difficulty match
        scored = self._score_by_difficulty(mode_missions, user_state.elo_rating)
        
        # 5. Select top candidates, add randomness
        top_candidates = scored[:5]  # Top 5 best matches
        selected = self._weighted_random_select(
            top_candidates, 
            user_state, 
            target_date
        )
        
        return selected
    
    def _get_available_missions(self, user_state: UserMissionState) -> List[MissionTemplate]:
        """Get missions for user's tier, excluding recently completed."""
        all_missions = self.mission_repo.get_by_tier(user_state.current_tier)
        
        # Exclude missions completed in last 30 days
        cutoff_date = date.today() - timedelta(days=30)
        recent_completed = {
            mid for mid in user_state.completed_mission_ids
            if self.mission_repo.get_completion_date(mid) > cutoff_date
        }
        
        # Also exclude missions not matching user's unlocked tags
        # (e.g., async missions only for Tier 3+)
        unlocked_tags = self._get_unlocked_tags(user_state.current_tier)
        
        return [
            m for m in all_missions
            if m.id not in recent_completed
            and all(tag in unlocked_tags for tag in m.tags)
        ]
    
    def _select_mode(self, tier: Tier) -> MissionMode:
        """Weighted random mode selection based on tier."""
        weights = MODE_WEIGHTS[tier]
        modes = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(modes, weights=probabilities, k=1)[0]
    
    def _score_by_difficulty(
        self, 
        missions: List[MissionTemplate], 
        user_elo: int
    ) -> List[MissionTemplate]:
        """
        Score missions by |mission_difficulty - user_elo|.
        Prefer missions within ±100 ELO of user.
        """
        def difficulty_score(mission: MissionTemplate) -> float:
            diff = abs(mission.difficulty_rating - user_elo)
            # Gaussian-like scoring: peak at 0, decay at ±200
            return math.exp(-(diff ** 2) / (2 * 100 ** 2))
        
        return sorted(missions, key=difficulty_score, reverse=True)
    
    def _weighted_random_select(
        self, 
        candidates: List[MissionTemplate],
        user_state: UserMissionState,
        target_date: date
    ) -> MissionTemplate:
        """
        Deterministic selection per user per day.
        Seed = hash(user_id + target_date) for reproducibility.
        """
        seed = hash(f"{user_state.user_id}{target_date.isoformat()}")
        rng = random.Random(seed)
        
        # Weight by difficulty score (already sorted)
        weights = [1.0 / (i + 1) for i in range(len(candidates))]
        return rng.choices(candidates, weights=weights, k=1)[0]
    
    def _get_unlocked_tags(self, tier: Tier) -> set[str]:
        """Tags unlocked at each tier."""
        tag_progression = {
            Tier.TIER_0: {"basic", "logic", "string", "loop", "function"},
            Tier.TIER_1: {"data_wrangling", "json", "csv", "error_handling", "big_o"},
            Tier.TIER_2: {"oop", "patterns", "typing", "testing", "logging", "pep8"},
            Tier.TIER_3: {"api", "async", "etl", "concurrency", "optimization"},
            Tier.TIER_4: {"refactoring", "debugging", "security", "architecture", "legacy"},
        }
        # Cumulative: Tier N includes all previous
        unlocked = set()
        for t in Tier:
            if t <= tier:
                unlocked.update(tag_progression[t])
        return unlocked
```

### 6.2.5 Boss Fight Generation (Weekly)

```python
class BossFightGenerator:
    """
    Generates weekly production incident scenario.
    Released Friday 19:00 WIB, deadline Sunday 23:59.
    """
    
    SCENARIOS = [
        {
            "id": "flash_sale_webhook",
            "title": "Flash Sale Webhook Parser Failure",
            "description": "E-commerce flash sale: webhook parser gagal parse JSON corrupt...",
            "time_limit_minutes": 20,
            "files": {
                "app/webhooks/parser.py": "BUGGY_CODE",
                "tests/test_webhook_parser.py": "HIDDEN_TESTS",
                "data/corrupt_payloads.json": "TEST_DATA",
            },
            "skills_tested": ["debugging", "error_handling", "json_parsing"],
            "tier_min": Tier.TIER_2,
        },
        {
            "id": "memory_leak_worker",
            "title": "Background Worker Memory Leak",
            "description": "Worker process memory grows unbounded...",
            "time_limit_minutes": 25,
            "files": {...},
            "skills_tested": ["profiling", "memory_management", "asyncio"],
            "tier_min": Tier.TIER_3,
        },
        # ... more scenarios
    ]
    
    def generate_weekly_boss_fight(self, week: str) -> BossFight:
        """Deterministic per week."""
        seed = hash(f"boss_fight_{week}")
        rng = random.Random(seed)
        scenario = rng.choice(self.SCENARIOS)
        
        return BossFight(
            week=week,
            scenario_id=scenario["id"],
            title=scenario["title"],
            description=scenario["description"],
            files=scenario["files"],
            time_limit_minutes=scenario["time_limit_minutes"],
            released_at=datetime.combine(
                self._get_friday_of_week(week), 
                time(19, 0)
            ),
            deadline=datetime.combine(
                self._get_sunday_of_week(week), 
                time(23, 59)
            ),
        )
```

---

## 6.3 Automated International Grader Algorithm

### 6.3.1 Requirements (from PRD 2.3.2)
Six-stage pipeline with weighted scoring:
1. **Lint** (ruff) - 15%
2. **Format** (ruff format) - 10%
3. **Type Check** (mypy --strict) - 20%
4. **Functional Test** (pytest) - 35%
5. **Performance** (custom benchmark) - 10%
6. **Code Quality** (complexity, naming) - 10%

Grade thresholds: S (≥95), A (≥85), B (≥75), C (≥65), F (<65)

### 6.3.2 Data Structures

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import time

class Grade(Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    F = "F"

class StageStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class StageResult:
    stage: str
    status: StageStatus
    score: float  # 0-100
    weight: float
    details: str
    execution_time_ms: int
    raw_output: Optional[str] = None

@dataclass
class GraderResult:
    mission_id: str
    user_id: str
    status: Grade
    total_score: float
    stage_results: List[StageResult]
    xp_earned: int
    elo_change: int
    skill_radar_delta: Dict[str, int]
    ai_review: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

# Stage weights (must sum to 1.0)
STAGE_WEIGHTS = {
    "lint": 0.15,
    "format": 0.10,
    "typecheck": 0.20,
    "functional": 0.35,
    "performance": 0.10,
    "quality": 0.10,
}

GRADE_THRESHOLDS = {
    Grade.S: 95,
    Grade.A: 85,
    Grade.B: 75,
    Grade.C: 65,
    Grade.F: 0,
}
```

### 6.3.3 Core Grading Pipeline

```python
class AutomatedGrader:
    """
    Executes 6-stage grading pipeline in sandbox.
    Fail-fast: if critical stage fails, skip remaining.
    """
    
    def __init__(
        self, 
        sandbox: SandboxRunner,
        config: GraderConfig
    ):
        self.sandbox = sandbox
        self.config = config
    
    async def grade_submission(
        self,
        mission: MissionTemplate,
        user_code: str,
        user_files: Dict[str, str],  # For multi-file
        user_tier: Tier
    ) -> GraderResult:
        """
        Main grading entry point.
        Returns GraderResult with all stage scores.
        """
        stage_results = []
        total_weighted_score = 0.0
        
        # Prepare sandbox environment
        sandbox_id = await self.sandbox.create_session(
            mission_id=mission.id,
            user_files=user_files,
            resource_limits=self._get_tier_limits(user_tier)
        )
        
        try:
            # Stage 1: Lint (ruff)
            result = await self._run_lint_stage(sandbox_id, mission)
            stage_results.append(result)
            total_weighted_score += result.score * result.weight
            
            if result.status == StageStatus.FAILED and self.config.fail_fast_lint:
                return self._finalize_failed(mission, stage_results, total_weighted_score)
            
            # Stage 2: Format Check
            result = await self._run_format_stage(sandbox_id, mission)
            stage_results.append(result)
            total_weighted_score += result.score * result.weight
            
            # Stage 3: Type Check (mypy --strict)
            result = await self._run_typecheck_stage(sandbox_id, mission)
            stage_results.append(result)
            total_weighted_score += result.score * result.weight
            
            if result.status == StageStatus.FAILED and self.config.fail_fast_type:
                return self._finalize_failed(mission, stage_results, total_weighted_score)
            
            # Stage 4: Functional Tests (pytest)
            result = await self._run_functional_stage(sandbox_id, mission)
            stage_results.append(result)
            total_weighted_score += result.score * result.weight
            
            if result.status == StageStatus.FAILED:
                return self._finalize_failed(mission, stage_results, total_weighted_score)
            
            # Stage 5: Performance Benchmark
            result = await self._run_performance_stage(sandbox_id, mission)
            stage_results.append(result)
            total_weighted_score += result.score * result.weight
            
            # Stage 6: Code Quality Analysis
            result = await self._run_quality_stage(sandbox_id, mission)
            stage_results.append(result)
            total_weighted_score += result.score * result.weight
            
            # Calculate final grade
            grade = self._calculate_grade(total_weighted_score)
            
            # Calculate rewards
            xp_earned = self._calculate_xp(mission, grade)
            elo_change = self._calculate_elo_change(grade, mission.difficulty_rating)
            skill_delta = self._calculate_skill_delta(stage_results, mission)
            
            # Generate AI review if grade >= B
            ai_review = None
            if grade in (Grade.S, Grade.A, Grade.B):
                ai_review = await self._generate_ai_review(mission, user_code, stage_results)
            
            return GraderResult(
                mission_id=mission.id,
                user_id="",  # Filled by caller
                status=grade,
                total_score=round(total_weighted_score, 2),
                stage_results=stage_results,
                xp_earned=xp_earned,
                elo_change=elo_change,
                skill_radar_delta=skill_delta,
                ai_review=ai_review,
            )
            
        finally:
            await self.sandbox.cleanup(sandbox_id)
    
    async def _run_lint_stage(self, sandbox_id: str, mission: MissionTemplate) -> StageResult:
        """Run ruff check on user code."""
        start = time.perf_counter()
        
        cmd = "ruff check . --output-format=json"
        result = await self.sandbox.execute(sandbox_id, cmd, timeout=30)
        
        execution_time = int((time.perf_counter() - start) * 1000)
        
        if result.exit_code == 0:
            return StageResult(
                stage="lint",
                status=StageStatus.PASSED,
                score=100.0,
                weight=STAGE_WEIGHTS["lint"],
                details="0 lint errors",
                execution_time_ms=execution_time,
                raw_output=result.stdout,
            )
        else:
            errors = json.loads(result.stdout)
            error_count = len(errors)
            # Score: 100 for 0, decaying with errors
            score = max(0, 100 - error_count * 10)
            return StageResult(
                stage="lint",
                status=StageStatus.FAILED,
                score=score,
                weight=STAGE_WEIGHTS["lint"],
                details=f"{error_count} lint errors",
                execution_time_ms=execution_time,
                raw_output=result.stdout,
            )
    
    async def _run_format_stage(self, sandbox_id: str, mission: MissionTemplate) -> StageResult:
        """Run ruff format --check."""
        start = time.perf_counter()
        
        cmd = "ruff format --check . --diff"
        result = await self.sandbox.execute(sandbox_id, cmd, timeout=30)
        
        execution_time = int((time.perf_counter() - start) * 1000)
        
        if result.exit_code == 0:
            return StageResult(
                stage="format",
                status=StageStatus.PASSED,
                score=100.0,
                weight=STAGE_WEIGHTS["format"],
                details="0 format diffs",
                execution_time_ms=execution_time,
            )
        else:
            # Count diff lines
            diff_lines = result.stdout.count('\n')
            score = max(0, 100 - diff_lines * 2)
            return StageResult(
                stage="format",
                status=StageStatus.FAILED,
                score=score,
                weight=STAGE_WEIGHTS["format"],
                details=f"{diff_lines} format diffs",
                execution_time_ms=execution_time,
                raw_output=result.stdout,
            )
    
    async def _run_typecheck_stage(self, sandbox_id: str, mission: MissionTemplate) -> StageResult:
        """Run mypy --strict."""
        start = time.perf_counter()
        
        cmd = "mypy --strict --show-error-codes . --exclude tests"
        result = await self.sandbox.execute(sandbox_id, cmd, timeout=60)
        
        execution_time = int((time.perf_counter() - start) * 1000)
        
        if result.exit_code == 0:
            return StageResult(
                stage="typecheck",
                status=StageStatus.PASSED,
                score=100.0,
                weight=STAGE_WEIGHTS["typecheck"],
                details="0 type errors",
                execution_time_ms=execution_time,
            )
        else:
            # Parse mypy JSON output
            errors = self._parse_mypy_errors(result.stdout)
            error_count = len(errors)
            score = max(0, 100 - error_count * 15)  # Type errors weighted heavier
            return StageResult(
                stage="typecheck",
                status=StageStatus.FAILED,
                score=score,
                weight=STAGE_WEIGHTS["typecheck"],
                details=f"{error_count} type errors",
                execution_time_ms=execution_time,
                raw_output=result.stdout,
            )
    
    async def _run_functional_stage(self, sandbox_id: str, mission: MissionTemplate) -> StageResult:
        """Run pytest with coverage."""
        start = time.perf_counter()
        
        # Run tests with JUnit XML output
        cmd = f"pytest {mission.test_file} -xvs --junitxml=test-results.xml --tb=short"
        result = await self.sandbox.execute(sandbox_id, cmd, timeout=120)
        
        execution_time = int((time.perf_counter() - start) * 1000)
        
        # Parse JUnit XML for detailed results
        test_results = self._parse_junit_xml("test-results.xml")
        passed = test_results["passed"]
        failed = test_results["failed"]
        total = test_results["total"]
        
        if failed == 0:
            return StageResult(
                stage="functional",
                status=StageStatus.PASSED,
                score=100.0,
                weight=STAGE_WEIGHTS["functional"],
                details=f"{passed}/{total} tests passed",
                execution_time_ms=execution_time,
            )
        else:
            # Partial credit based on pass rate
            pass_rate = passed / total if total > 0 else 0
            score = round(pass_rate * 100, 1)
            return StageResult(
                stage="functional",
                status=StageStatus.FAILED,
                score=score,
                weight=STAGE_WEIGHTS["functional"],
                details=f"{passed}/{total} tests passed ({failed} failed)",
                execution_time_ms=execution_time,
                raw_output=result.stdout,
            )
    
    async def _run_performance_stage(self, sandbox_id: str, mission: MissionTemplate) -> StageResult:
        """Run performance benchmark against thresholds."""
        start = time.perf_counter()
        
        # Run custom benchmark script
        cmd = f"python -m pytest {mission.test_file}::test_performance -xvs --benchmark-json=bench.json"
        result = await self.sandbox.execute(sandbox_id, cmd, timeout=60)
        
        execution_time = int((time.perf_counter() - start) * 1000)
        
        if result.exit_code == 0:
            bench_data = self._parse_benchmark_json("bench.json")
            # Compare against tier-specific thresholds
            thresholds = self._get_performance_thresholds(mission.tier)
            score = self._calculate_performance_score(bench_data, thresholds)
            
            return StageResult(
                stage="performance",
                status=StageStatus.PASSED if score >= 70 else StageStatus.FAILED,
                score=score,
                weight=STAGE_WEIGHTS["performance"],
                details=f"Time: {bench_data['mean_time_ms']}ms, Memory: {bench_data['peak_memory_mb']}MB",
                execution_time_ms=execution_time,
            )
        else:
            # No performance test defined or failed to run
            return StageResult(
                stage="performance",
                status=StageStatus.SKIPPED,
                score=50.0,  # Neutral score
                weight=STAGE_WEIGHTS["performance"],
                details="Performance test not available or failed",
                execution_time_ms=execution_time,
            )
    
    async def _run_quality_stage(self, sandbox_id: str, mission: MissionTemplate) -> StageResult:
        """Analyze code quality metrics."""
        start = time.perf_counter()
        
        # Run custom quality analyzer (radon, xenon, custom rules)
        cmd = "python -m pyforge.quality_analyzer . --format=json"
        result = await self.sandbox.execute(sandbox_id, cmd, timeout=30)
        
        execution_time = int((time.perf_counter() - start) * 1000)
        
        if result.exit_code == 0:
            quality_data = json.loads(result.stdout)
            score = quality_data["overall_score"]  # 0-100
            
            return StageResult(
                stage="quality",
                status=StageStatus.PASSED if score >= 85 else StageStatus.FAILED,
                score=score,
                weight=STAGE_WEIGHTS["quality"],
                details=f"CC: {quality_data['avg_cyclomatic_complexity']:.1f}, "
                        f"Nesting: {quality_data['max_nesting_depth']}, "
                        f"Naming: {quality_data['naming_score']}",
                execution_time_ms=execution_time,
            )
        else:
            return StageResult(
                stage="quality",
                status=StageStatus.ERROR,
                score=0.0,
                weight=STAGE_WEIGHTS["quality"],
                details="Quality analyzer failed",
                execution_time_ms=execution_time,
                raw_output=result.stderr,
            )
    
    def _calculate_grade(self, weighted_score: float) -> Grade:
        for grade, threshold in sorted(GRADE_THRESHOLDS.items(), key=lambda x: -x[1]):
            if weighted_score >= threshold:
                return grade
        return Grade.F
    
    def _calculate_xp(self, mission: MissionTemplate, grade: Grade) -> int:
        """XP based on mission base XP and grade multiplier."""
        multipliers = {
            Grade.S: 1.5,
            Grade.A: 1.2,
            Grade.B: 1.0,
            Grade.C: 0.7,
            Grade.F: 0.0,
        }
        return int(mission.xp_reward * multipliers[grade])
    
    def _calculate_elo_change(self, grade: Grade, mission_difficulty: int) -> int:
        """ELO change based on grade and difficulty."""
        base_changes = {
            Grade.S: 25,
            Grade.A: 15,
            Grade.B: 8,
            Grade.C: 3,
            Grade.F: -10,
        }
        return base_changes[grade]
    
    def _calculate_skill_delta(
        self, 
        stage_results: List[StageResult], 
        mission: MissionTemplate
    ) -> Dict[str, int]:
        """Map stage results to skill radar dimensions."""
        deltas = {dim: 0 for dim in ["logic", "clean_code", "debugging", "testing", "performance"]}
        
        # Mapping: stage → skill dimensions
        stage_to_skills = {
            "lint": {"clean_code": 3},
            "format": {"clean_code": 2},
            "typecheck": {"clean_code": 2, "logic": 1},
            "functional": {"logic": 3, "testing": 2, "debugging": 1},
            "performance": {"performance": 3, "logic": 1},
            "quality": {"clean_code": 2, "logic": 1},
        }
        
        for result in stage_results:
            if result.status == StageStatus.PASSED:
                for skill, delta in stage_to_skills.get(result.stage, {}).items():
                    deltas[skill] += delta
            elif result.status == StageStatus.FAILED:
                # Small penalty for failures
                for skill in stage_to_skills.get(result.stage, {}):
                    deltas[skill] = max(0, deltas[skill] - 1)
        
        return deltas
```

---

## 6.4 ELO Rating & Skill Radar Algorithm

### 6.4.1 ELO Rating System (PRD 2.2.3)

```python
class EloRatingSystem:
    """
    ELO rating for skill-based matchmaking and tier progression.
    """
    
    # Tier unlock thresholds (from PRD)
    TIER_THRESHOLDS = {
        Tier.TIER_0: 0,
        Tier.TIER_1: 1100,
        Tier.TIER_2: 1250,
        Tier.TIER_3: 1400,
        Tier.TIER_4: 1600,
    }
    
    # K-factor based on rating (standard chess adaptation)
    def get_k_factor(self, rating: int, games_played: int) -> int:
        if games_played < 30:
            return 32  # New players: volatile
        elif rating < 1400:
            return 24  # Developing
        elif rating < 1600:
            return 16  # Established
        else:
            return 10  # Expert: stable
    
    def calculate_rating_change(
        self, 
        player_rating: int, 
        mission_difficulty: int, 
        grade: Grade,
        games_played: int
    ) -> int:
        """
        ELO update based on mission performance.
        Expected score based on rating difference.
        """
        k = self.get_k_factor(player_rating, games_played)
        
        # Expected score (logistic curve)
        expected = 1 / (1 + 10 ** ((mission_difficulty - player_rating) / 400))
        
        # Actual score based on grade
        grade_scores = {
            Grade.S: 1.0,
            Grade.A: 0.8,
            Grade.B: 0.6,
            Grade.C: 0.4,
            Grade.F: 0.0,
        }
        actual = grade_scores[grade]
        
        # Standard ELO formula
        change = round(k * (actual - expected))
        
        # Clamp to reasonable bounds per grade
        max_changes = {Grade.S: 30, Grade.A: 20, Grade.B: 15, Grade.C: 10, Grade.F: -20}
        return max(min(change, max_changes[grade]), -20 if grade == Grade.F else -5)
    
    def get_tier_for_rating(self, rating: int) -> Tier:
        """Determine tier from current rating."""
        for tier in reversed(Tier):
            if rating >= self.TIER_THRESHOLDS[tier]:
                return tier
        return Tier.TIER_0
```

### 6.4.2 Skill Radar (5 Dimensions)

```python
class SkillRadar:
    """
    Tracks 5 competency dimensions (0-100 each).
    Updated after each mission based on grader stage results.
    """
    
    DIMENSIONS = [
        "logic",           # Algorithmic thinking, problem decomposition
        "clean_code",      # PEP 8, naming, structure, SOLID
        "debugging",       # Root cause analysis, logging, reproducible tests
        "testing",         # Test design, mocking, edge cases, coverage
        "performance",     # Big-O awareness, profiling, optimization
    ]
    
    # Decay factor for inactive skills (per day)
    DAILY_DECAY = 0.001  # 0.1% per day
    
    # Maximum skill level
    MAX_SKILL = 100
    
    def __init__(self):
        self.skills: Dict[str, float] = {d: 0.0 for d in self.DIMENSIONS}
        self.last_updated: Dict[str, date] = {d: date.today() for d in self.DIMENSIONS}
    
    def apply_daily_decay(self, current_date: date):
        """Apply decay for days since last update."""
        for dim in self.DIMENSIONS:
            days_inactive = (current_date - self.last_updated[dim]).days
            if days_inactive > 0:
                decay_factor = (1 - self.DAILY_DECAY) ** days_inactive
                self.skills[dim] *= decay_factor
    
    def update_from_mission(self, skill_delta: Dict[str, int]):
        """Apply skill changes from mission completion."""
        for dim, delta in skill_delta.items():
            if dim in self.skills:
                old_value = self.skills[dim]
                new_value = min(self.MAX_SKILL, max(0, old_value + delta))
                self.skills[dim] = new_value
                self.last_updated[dim] = date.today()
    
    def get_radar_data(self) -> Dict[str, float]:
        """Return current skill levels for visualization."""
        return {dim: round(self.skills[dim], 1) for dim in self.DIMENSIONS}
    
    def get_overall_score(self) -> float:
        """Weighted average (equal weights for radar display)."""
        return round(sum(self.skills.values()) / len(self.skills), 1)
    
    def get_strongest_weakest(self) -> tuple[str, str]:
        """Return strongest and weakest dimensions."""
        sorted_skills = sorted(self.skills.items(), key=lambda x: x[1])
        return sorted_skills[-1][0], sorted_skills[0][0]
```

---

## 6.5 Streak & Gamification Mechanics

### 6.5.1 Streak System (PRD 2.3.1)

```python
class StreakManager:
    """
    Manages daily streak, freeze shields, and streak bonuses.
    """
    
    # Streak milestones and rewards
    STREAK_REWARDS = {
        7: {"xp": 500, "badge": "week_warrior"},
        14: {"xp": 1000, "badge": "fortnight_fighter"},
        30: {"xp": 5000, "badge": "month_master"},
        60: {"xp": 10000, "badge": "streak_legend"},
        100: {"xp": 25000, "badge": "centurion"},
        365: {"xp": 100000, "badge": "year_of_code"},
    }
    
    # Freeze shield: 1 per week (claimable Sat/Sun)
    FREEZE_SHIELD_WEEKLY = 1
    MAX_FREEZE_SHIELDS = 3  # Cap
    
    def __init__(self):
        self.current_streak = 0
        self.longest_streak = 0
        self.freeze_shields = 0
        self.last_mission_date: Optional[date] = None
        self.freeze_shield_claimed_this_week = False
        self.week_start_date = self._get_week_start(date.today())
    
    def _get_week_start(self, d: date) -> date:
        """Monday as week start."""
        return d - timedelta(days=d.weekday())
    
    def record_mission_completion(self, completion_date: date) -> StreakResult:
        """
        Call when user completes daily mission.
        Returns streak changes and rewards.
        """
        # Check for new week (reset freeze claim)
        week_start = self._get_week_start(completion_date)
        if week_start != self.week_start_date:
            self.week_start_date = week_start
            self.freeze_shield_claimed_this_week = False
            # Grant weekly freeze shield
            self.freeze_shields = min(
                self.MAX_FREEZE_SHIELDS, 
                self.freeze_shields + self.FREEZE_SHIELD_WEEKLY
            )
        
        # Calculate days since last mission
        if self.last_mission_date is None:
            # First mission ever
            days_gap = 0
        else:
            days_gap = (completion_date - self.last_mission_date).days
        
        freeze_used = False
        streak_broken = False
        rewards = []
        
        if days_gap == 0:
            # Same day (multiple missions? shouldn't happen but handle)
            pass
        elif days_gap == 1:
            # Consecutive day - streak continues
            self.current_streak += 1
        else:
            # Gap > 1 day
            if self.freeze_shields > 0 and days_gap <= 2:
                # Use freeze shield for 1-day gap
                self.freeze_shields -= 1
                freeze_used = True
                self.current_streak += 1
            else:
                # Streak broken
                streak_broken = True
                self.current_streak = 1  # Reset to 1 (today counts)
        
        # Update longest streak
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        # Check milestone rewards
        if self.current_streak in self.STREAK_REWARDS:
            reward = self.STREAK_REWARDS[self.current_streak]
            rewards.append(reward)
        
        self.last_mission_date = completion_date
        
        return StreakResult(
            current_streak=self.current_streak,
            longest_streak=self.longest_streak,
            freeze_shields_remaining=self.freeze_shields,
            freeze_used=freeze_used,
            streak_broken=streak_broken,
            rewards=rewards,
        )
    
    def claim_freeze_shield(self, claim_date: date) -> bool:
        """Claim weekly freeze shield (Sat/Sun only)."""
        # Only allow on weekend (5=Sat, 6=Sun)
        if claim_date.weekday() not in (5, 6):
            return False
        
        if self.freeze_shield_claimed_this_week:
            return False
        
        self.freeze_shields = min(self.MAX_FREEZE_SHIELDS, self.freeze_shields + 1)
        self.freeze_shield_claimed_this_week = True
        return True
```

---

## 6.6 AI Provider Routing & Fallback Algorithm

### 6.6.1 Requirements (PRD 2.3.3)
- Support multiple providers: 9Router, Ollama, LM Studio, OpenAI, Anthropic, Custom
- 9Router default: `http://127.0.0.1:20128/v1` with fallback combo
- Health check before session
- Automatic fallback on failure
- Rate limit handling (429) with exponential backoff

### 6.6.2 Core Routing Logic

```python
from dataclasses import dataclass
from typing import List, Optional, AsyncGenerator
import asyncio
import time
from enum import Enum

class ProviderType(Enum):
    NINE_ROUTER = "9router"
    OLLAMA = "ollama"
    LM_STUDIO = "lmstudio"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"

@dataclass
class ProviderConfig:
    id: str
    type: ProviderType
    name: str
    base_url: str
    api_key: str  # Encrypted at rest
    model: str
    fallback_models: List[str] = field(default_factory=list)
    timeout: float = 30.0
    max_retries: int = 3
    is_default: bool = False
    priority: int = 0  # Lower = higher priority

@dataclass
class AIRequest:
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    role: str = "socratic"  # socratic, reviewer, generator

@dataclass
class AIResponse:
    content: str
    model: str
    provider_id: str
    usage: Dict[str, int]
    latency_ms: int

class AIProviderRouter:
    """
    Routes AI requests to configured providers with fallback chain.
    """
    
    def __init__(self, configs: List[ProviderConfig]):
        self.providers = {c.id: c for c in configs}
        self.default_provider = next(
            (c for c in configs if c.is_default), 
            configs[0] if configs else None
        )
        # Circuit breaker state
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            pid: CircuitBreaker() for pid in self.providers
        }
    
    async def execute_request(
        self, 
        request: AIRequest,
        provider_id: Optional[str] = None
    ) -> AIResponse:
        """
        Execute request with automatic fallback.
        Tries primary provider, then fallbacks in priority order.
        """
        # Determine provider chain
        if provider_id and provider_id in self.providers:
            chain = [provider_id] + self._get_fallback_chain(provider_id)
        else:
            chain = self._get_fallback_chain(self.default_provider.id) if self.default_provider else []
        
        last_error = None
        
        for pid in chain:
            provider = self.providers[pid]
            breaker = self.circuit_breakers[pid]
            
            # Check circuit breaker
            if breaker.is_open:
                continue
            
            try:
                response = await self._execute_with_retry(provider, request)
                breaker.record_success()
                return response
            except RateLimitError as e:
                # Special handling: wait and retry same provider
                await self._handle_rate_limit(provider, e)
                try:
                    response = await self._execute_with_retry(provider, request)
                    breaker.record_success()
                    return response
                except Exception as e2:
                    last_error = e2
                    breaker.record_failure()
            except Exception as e:
                last_error = e
                breaker.record_failure()
                continue
        
        raise AIProviderError(f"All providers failed. Last error: {last_error}")
    
    async def _execute_with_retry(
        self, 
        provider: ProviderConfig, 
        request: AIRequest
    ) -> AIResponse:
        """Execute with exponential backoff retry."""
        last_error = None
        
        for attempt in range(provider.max_retries):
            try:
                return await self._call_provider(provider, request)
            except (TimeoutError, ConnectionError) as e:
                last_error = e
                if attempt < provider.max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(wait_time)
            except RateLimitError:
                raise  # Re-raise for special handling
        
        raise last_error or Exception("Max retries exceeded")
    
    async def _call_provider(
        self, 
        provider: ProviderConfig, 
        request: AIRequest
    ) -> AIResponse:
        """Make actual HTTP call to provider."""
        start = time.perf_counter()
        
        # Build request payload
        payload = {
            "model": request.model or provider.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "stream": request.stream,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        }
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=provider.timeout)
        ) as session:
            url = f"{provider.base_url.rstrip('/')}/chat/completions"
            
            if request.stream:
                return await self._stream_response(session, url, headers, payload, provider.id, start)
            else:
                return await self._single_response(session, url, headers, payload, provider.id, start)
    
    async def _single_response(
        self, 
        session: aiohttp.ClientSession,
        url: str,
        headers: Dict,
        payload: Dict,
        provider_id: str,
        start: float
    ) -> AIResponse:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                raise RateLimitError(retry_after=retry_after)
            
            resp.raise_for_status()
            data = await resp.json()
            
            latency_ms = int((time.perf_counter() - start) * 1000)
            
            return AIResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                provider_id=provider_id,
                usage=data.get("usage", {}),
                latency_ms=latency_ms,
            )
    
    def _get_fallback_chain(self, primary_id: str) -> List[str]:
        """Get ordered fallback providers."""
        primary = self.providers[primary_id]
        
        # For 9Router, use configured fallback models first
        if primary.type == ProviderType.NINE_ROUTER and primary.fallback_models:
            # Return same provider with different models
            return [primary_id]  # Model switching handled at request level
        
        # Otherwise, other providers sorted by priority
        others = [
            p for p in self.providers.values() 
            if p.id != primary_id
        ]
        return sorted(others, key=lambda p: p.priority)

class CircuitBreaker:
    """Prevents cascading failures to unhealthy providers."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
    
    @property
    def is_open(self) -> bool:
        if self.state == "open":
            # Check if recovery timeout passed
            if self.last_failure_time and \
               time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                return False
            return True
        return False
    
    def record_success(self):
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
```

---

## 6.7 Sandbox Security & Resource Management

### 6.7.1 Requirements (PRD 2.4)
- `--network=none`, `--read-only` filesystem
- RAM 128-256MB, CPU limit, timeout 5s
- Prevent RCE, fork bombs, network access, file system escape

### 6.7.2 Sandbox Configuration

```python
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class SandboxLimits:
    """Resource limits per tier."""
    memory_mb: int
    cpu_cores: float
    timeout_seconds: int
    pids_limit: int
    disk_mb: int

# Tier-based limits (stricter for lower tiers)
TIER_LIMITS = {
    Tier.TIER_0: SandboxLimits(
        memory_mb=64,
        cpu_cores=0.5,
        timeout_seconds=3,
        pids_limit=32,
        disk_mb=10,
    ),
    Tier.TIER_1: SandboxLimits(
        memory_mb=128,
        cpu_cores=1.0,
        timeout_seconds=5,
        pids_limit=64,
        disk_mb=50,
    ),
    Tier.TIER_2: SandboxLimits(
        memory_mb=256,
        cpu_cores=1.5,
        timeout_seconds=10,
        pids_limit=128,
        disk_mb=100,
    ),
    Tier.TIER_3: SandboxLimits(
        memory_mb=512,
        cpu_cores=2.0,
        timeout_seconds=30,
        pids_limit=256,
        disk_mb=200,
    ),
    Tier.TIER_4: SandboxLimits(
        memory_mb=512,
        cpu_cores=2.0,
        timeout_seconds=60,
        pids_limit=256,
        disk_mb=500,
    ),
}

class SandboxRunner:
    """
    Manages isolated Docker containers for code execution.
    Uses gVisor (runsc) for additional isolation.
    """
    
    # Forbidden syscalls and patterns
    FORBIDDEN_PATTERNS = [
        r"os\.system",
        r"subprocess\.",
        r"multiprocessing\.",
        r"threading\.",
        r"socket\.",
        r"urllib\.",
        r"requests\.",
        r"http\.",
        r"ftplib\.",
        r"telnetlib\.",
        r"eval\(",
        r"exec\(",
        r"compile\(",
        r"__import__\(",
        r"open\([^)]*[\"']/etc/",
        r"open\([^)]*[\"']/proc/",
        r"open\([^)]*[\"']/sys/",
    ]
    
    def __init__(self, docker_client: DockerClient):
        self.docker = docker_client
        self.image = "pyforge/sandbox-runner:latest"
    
    async def create_session(
        self,
        mission_id: str,
        user_files: Dict[str, str],
        resource_limits: SandboxLimits
    ) -> str:
        """Create isolated container session."""
        # Write user files to temp directory
        host_dir = tempfile.mkdtemp(prefix=f"pyforge_{mission_id}_")
        for path, content in user_files.items():
            full_path = Path(host_dir) / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Create container with strict limits
        container = self.docker.containers.run(
            self.image,
            command="sleep infinity",  # Keep alive for multiple execs
            detach=True,
            # Security
            network_mode="none",
            read_only=True,
            cap_drop=["ALL"],
            security_opt=["no-new-privileges:true"],
            # Resources
            mem_limit=f"{resource_limits.memory_mb}m",
            memswap_limit=f"{resource_limits.memory_mb}m",
            cpu_quota=int(resource_limits.cpu_cores * 100000),
            cpu_period=100000,
            pids_limit=resource_limits.pids_limit,
            # Volumes
            volumes={
                host_dir: {"bind": "/workspace", "mode": "rw"},
            },
            working_dir="/workspace",
            # gVisor runtime
            runtime="runsc",
            # Tempfs for writable directories
            tmpfs={
                "/tmp": "size=10m,noexec,nosuid,nodev",
                "/home/sandbox": "size=50m,noexec,nosuid,nodev",
            },
            user="sandbox",  # Non-root user
        )
        
        # Store session metadata
        session_id = container.id[:12]
        self._sessions[session_id] = {
            "container": container,
            "host_dir": host_dir,
            "created_at": time.time(),
            "limits": resource_limits,
        }
        
        return session_id
    
    async def execute(
        self, 
        session_id: str, 
        command: str, 
        timeout: int = 30
    ) -> ExecutionResult:
        """Execute command in sandbox container."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        container = session["container"]
        limits = session["limits"]
        
        # Pre-flight: static analysis for forbidden patterns
        if self._contains_forbidden(command):
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr="Forbidden operation detected",
                status="blocked",
            )
        
        # Execute with timeout
        try:
            exec_result = container.exec_run(
                cmd=["/bin/sh", "-c", command],
                timeout=min(timeout, limits.timeout_seconds),
                demux=True,  # Separate stdout/stderr
            )
            
            stdout = exec_result.output[0].decode() if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode() if exec_result.output[1] else ""
            
            return ExecutionResult(
                exit_code=exec_result.exit_code,
                stdout=stdout,
                stderr=stderr,
                status="completed" if exec_result.exit_code == 0 else "error",
            )
            
        except Exception as e:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                status="timeout" if "timeout" in str(e).lower() else "error",
            )
    
    def _contains_forbidden(self, code: str) -> bool:
        """Static check for forbidden patterns."""
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code):
                return True
        return False
    
    async def cleanup(self, session_id: str):
        """Clean up container and temp files."""
        session = self._sessions.pop(session_id, None)
        if session:
            try:
                session["container"].stop(timeout=1)
                session["container"].remove()
            except:
                pass
            # Clean up host directory
            shutil.rmtree(session["host_dir"], ignore_errors=True)
```

---

## 6.8 Curriculum Progression & Adaptive Difficulty

### 6.8.1 Tier Progression Logic

```python
class CurriculumEngine:
    """
    Manages curriculum progression, tier unlocks, and adaptive difficulty.
    """
    
    TIER_REQUIREMENTS = {
        Tier.TIER_0: {"min_elo": 0, "min_missions": 0},
        Tier.TIER_1: {"min_elo": 1100, "min_missions": 10},
        Tier.TIER_2: {"min_elo": 1250, "min_missions": 25},
        Tier.TIER_3: {"min_elo": 1400, "min_missions": 50},
        Tier.TIER_4: {"min_elo": 1600, "min_missions": 100},
    }
    
    def __init__(self, mission_repo: MissionRepository):
        self.mission_repo = mission_repo
    
    def check_tier_unlock(self, user_stats: UserStats) -> Optional[Tier]:
        """Check if user qualifies for next tier."""
        current_tier = user_stats.current_tier
        next_tier = Tier(current_tier + 1)
        
        if next_tier > Tier.TIER_4:
            return None
        
        req = self.TIER_REQUIREMENTS[next_tier]
        
        if user_stats.elo_rating >= req["min_elo"] and \
           user_stats.completed_missions >= req["min_missions"]:
            return next_tier
        
        return None
    
    def get_adaptive_mission_pool(
        self, 
        user_stats: UserStats,
        pool_size: int = 20
    ) -> List[MissionTemplate]:
        """
        Get personalized mission pool based on:
        - Current tier
        - Weak skill dimensions (target practice)
        - Recent performance trends
        """
        # Base pool: current tier missions
        pool = self.mission_repo.get_by_tier(user_stats.current_tier)
        
        # Boost missions targeting weak skills
        weak_skills = self._identify_weak_skills(user_stats.skill_radar)
        if weak_skills:
            skill_tagged = self.mission_repo.get_by_tags(weak_skills)
            pool = skill_tagged + pool
        
        # Remove recently completed
        recent = user_stats.recent_mission_ids(last_days=14)
        pool = [m for m in pool if m.id not in recent]
        
        # Shuffle and limit
        random.shuffle(pool)
        return pool[:pool_size]
    
    def _identify_weak_skills(self, skill_radar: SkillRadar) -> List[str]:
        """Return tags for bottom 2 skills."""
        sorted_skills = sorted(skill_radar.skills.items(), key=lambda x: x[1])
        weakest = [s[0] for s in sorted_skills[:2]]
        
        skill_to_tags = {
            "logic": ["algorithm", "problem_solving", "recursion"],
            "clean_code": ["pep8", "naming", "refactoring", "patterns"],
            "debugging": ["error_handling", "logging", "testing"],
            "testing": ["pytest", "mocking", "edge_cases", "coverage"],
            "performance": ["big_o", "async", "optimization", "profiling"],
        }
        
        tags = []
        for skill in weakest:
            tags.extend(skill_to_tags.get(skill, []))
        return tags
```

---

## 6.9 Summary: Algorithm Integration Points

| Algorithm | Input | Output | Called By |
|---|---|---|---|
| **DailyMissionGenerator** | UserState, Date | MissionTemplate | Scheduler (00:00 WIB) |
| **AutomatedGrader** | Mission, UserCode, Files | GraderResult | API `/submit` |
| **EloRatingSystem** | Rating, Difficulty, Grade | EloChange | GraderResult processor |
| **SkillRadar** | StageResults, Mission | SkillDeltas | GraderResult processor |
| **StreakManager** | CompletionDate | StreakResult | Daily mission completion |
| **AIProviderRouter** | Request, ProviderChain | AIResponse | Hint/Review/Generate APIs |
| **SandboxRunner** | Code, Limits | ExecutionResult | Grader, Pyodide fallback |
| **CurriculumEngine** | UserStats | MissionPool, TierUnlock | Mission generator, Dashboard |

---

*Document Version: 1.0 | Created: 2026-01-17 | Based on BRD v1.0, PRD v1.0*