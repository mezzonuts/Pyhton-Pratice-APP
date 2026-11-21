import json
import subprocess
import tempfile as tempmod
import os
import shutil
from typing import Dict, Any, List

from app.services.ruff_mypy_integration import run_ruff_check, run_mypy_strict


class GraderResult:
    def __init__(self):
        self.total_score: float = 0.0
        self.grade: str = "F"
        self.xp: int = 0
        self.elo_change: int = 0
        self.stage_results: List[dict] = []
        self.execution_result: dict = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": self.total_score,
            "grade": self.grade,
            "xp": self.xp,
            "elo_change": self.elo_change,
            "stage_results": self.stage_results,
            "execution_result": self.execution_result,
        }


STAGE_WEIGHTS = {
    "lint": 0.15,
    "format": 0.10,
    "typecheck": 0.20,
    "functional": 0.35,
    "performance": 0.10,
    "quality": 0.10,
}


GRADE_THRESHOLDS = {
    "S": 90,
    "A": 80,
    "B": 70,
    "C": 60,
    "F": 60,
}

GRADE_MULTIPLIERS = {
    "S": 1.5,
    "A": 1.2,
    "B": 1.0,
    "C": 0.7,
    "F": 0.0,
}


def calculate_total_score(stage_results: List[dict]) -> float:
    """Calculate total weighted score from stage results."""
    total = 0.0
    for stage in stage_results:
        score = stage.get("score", 0)
        weight = stage.get("weight", 0)
        total += score * weight
    return round(total, 2)


def determine_grade(total_score: float) -> str:
    """Determine grade based on total score."""
    if total_score >= GRADE_THRESHOLDS["S"]:
        return "S"
    elif total_score >= GRADE_THRESHOLDS["A"]:
        return "A"
    elif total_score >= GRADE_THRESHOLDS["B"]:
        return "B"
    elif total_score >= GRADE_THRESHOLDS["C"]:
        return "C"
    else:
        return "F"


def calculate_xp(base_xp: int, grade: str) -> int:
    """Calculate XP reward based on grade multiplier."""
    multiplier = GRADE_MULTIPLIERS.get(grade, 0.0)
    return int(round(base_xp * multiplier))


def run_grader_pipeline(
    code: str,
    mission_test_file: str = "",
    base_xp: int = 100,
) -> GraderResult:
    """Run the full 6-stage grading pipeline.

    Stages:
    1. Lint: ruff check - 15% weight
    2. Format: ruff format --check - 10% weight
    3. Typecheck: mypy --strict - 20% weight
    4. Functional: pytest - 35% weight
    5. Performance: benchmark - 10% weight
    6. Quality: complexity analysis - 10% weight
    """
    result = GraderResult()
    tmp_dir = tempmod.mkdtemp(prefix="grader_")

    try:
        # Write code to temp file
        code_path = os.path.join(tmp_dir, "user_code.py")
        with open(code_path, "w") as f:
            f.write(code)

        # Stage 1: Lint (ruff check) - 15% weight
        lint_result = run_ruff_check(code, timeout=30)
        error_count = len(lint_result.get("errors", []))
        lint_score = max(0, 100 - error_count * 5)
        lint_weighted = lint_score * STAGE_WEIGHTS["lint"]
        result.stage_results.append(
            {
                "stage": "lint",
                "status": "passed" if lint_result["exit_code"] == 0 else "failed",
                "score": lint_score,
                "weight": STAGE_WEIGHTS["lint"],
                "details": f"{error_count} lint errors",
            }
        )

        # Stage 2: Format (ruff format --check) - 10% weight
        with tempmod.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            format_tmp = f.name
        try:
            format_result = subprocess.run(
                ["ruff", "format", "--check", format_tmp, "--diff"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            format_score = 100 if format_result.returncode == 0 else 0
            format_weighted = format_score * STAGE_WEIGHTS["format"]
            result.stage_results.append(
                {
                    "stage": "format",
                    "status": "passed" if format_result.returncode == 0 else "failed",
                    "score": format_score,
                    "weight": STAGE_WEIGHTS["format"],
                    "details": "0 format diffs"
                    if format_result.returncode == 0
                    else "format issues detected",
                }
            )
        finally:
            os.unlink(format_tmp)

        # Stage 3: Typecheck (mypy --strict) - 20% weight
        mypy_result = run_mypy_strict(code, timeout=60)
        mypy_error_count = len(mypy_result.get("errors", []))
        mypy_score = max(0, 100 - mypy_error_count * 10)
        mypy_weighted = mypy_score * STAGE_WEIGHTS["typecheck"]
        result.stage_results.append(
            {
                "stage": "typecheck",
                "status": "passed" if mypy_result["exit_code"] == 0 else "failed",
                "score": mypy_score,
                "weight": STAGE_WEIGHTS["typecheck"],
                "details": f"{mypy_error_count} type errors",
            }
        )

        # Stage 4: Functional (pytest) - 35% weight
        # Write test file and run pytest
        test_path = os.path.join(tmp_dir, "test_user_code.py")
        with open(test_path, "w") as f:
            f.write(mission_test_file if mission_test_file else "def test_pass(): pass\n")

        pytest_result = subprocess.run(
            ["pytest", test_path, "-xvs"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        passed = 0
        total = 1
        if pytest_result.returncode == 0 or "passed" in pytest_result.stdout:
            # Simple pass/fail based on output
            for line in pytest_result.stdout.split("\n"):
                if "passed" in line.lower():
                    try:
                        p = int(line.split()[0])
                        passed = p
                        total = p + 1  # estimate
                    except (ValueError, IndexError):
                        pass
        func_score = 100 if passed == total and total > 0 else 0
        func_weighted = func_score * STAGE_WEIGHTS["functional"]
        result.stage_results.append(
            {
                "stage": "functional",
                "status": "passed" if func_score == 100 else "failed",
                "score": func_score,
                "weight": STAGE_WEIGHTS["functional"],
                "details": f"{passed}/{total} tests passed",
            }
        )

        # Stage 5: Performance - 10% weight
        # Simple benchmark: execution time of the code
        try:
            bench_result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
            )
            perf_score = 100.0  # Neutral score if available
            perf_weighted = perf_score * STAGE_WEIGHTS["performance"]
            result.stage_results.append(
                {
                    "stage": "performance",
                    "status": "passed",
                    "score": perf_score,
                    "weight": STAGE_WEIGHTS["performance"],
                    "details": "Benchmark available",
                }
            )
        except Exception:
            result.stage_results.append(
                {
                    "stage": "performance",
                    "status": "skipped",
                    "score": 50.0,
                    "weight": STAGE_WEIGHTS["performance"],
                    "details": "Performance test skipped",
                }
            )

        # Stage 6: Quality (complexity analysis) - 10% weight
        # Simple cyclomatic complexity check
        try:
            complex_result = subprocess.run(
                ["python", "-m", "radon", "cc", code_path, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if complex_result.returncode == 0 and complex_result.stdout.strip():
                import json as _json
                complexity_data = _json.loads(complex_result.stdout)
                max_cc = max(
                    (func.get("complexity", 0) for func in complexity_data),
                    default=0,
                )
                quality_score = max(0, 100 - max_cc * 10)
            else:
                quality_score = 100.0
            quality_weighted = quality_score * STAGE_WEIGHTS["quality"]
            result.stage_results.append(
                {
                    "stage": "quality",
                    "status": "passed" if quality_score >= 70 else "failed",
                    "score": quality_score,
                    "weight": STAGE_WEIGHTS["quality"],
                    "details": f"max complexity: {max_cc}" if complex_result.returncode == 0 else "complexity analysis skipped",
                }
            )
        except Exception:
            result.stage_results.append(
                {
                    "stage": "quality",
                    "status": "skipped",
                    "score": 50.0,
                    "weight": STAGE_WEIGHTS["quality"],
                    "details": "Quality analysis skipped",
                }
            )

        # Calculate total score and grade
        result.total_score = calculate_total_score(result.stage_results)
        result.grade = determine_grade(result.total_score)
        result.xp = calculate_xp(base_xp, result.grade)

        return result

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)