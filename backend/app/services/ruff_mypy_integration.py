import json
import subprocess
import tempfile
import os
from typing import List, Dict, Any


def run_ruff_check(code: str, timeout: int = 30) -> dict:
    """Run ruff check on code written to a temp file.

    Returns dict with {errors: list, exit_code: int}
    """
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["ruff", "check", tmp_path, "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        try:
            errors = json.loads(result.stdout) if result.stdout.strip() else []
        except (json.JSONDecodeError, ValueError):
            errors = []

        return {"errors": errors, "exit_code": result.returncode}
    finally:
        os.unlink(tmp_path)


def run_mypy_strict(code: str, timeout: int = 60) -> dict:
    """Run mypy --strict on code written to a temp file.

    Returns dict with {errors: list, exit_code: int}
    """
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["mypy", "--strict", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        # Parse mypy output - each error line starts with file path followed by error code
        errors = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                errors.append(line.strip())

        return {"errors": errors, "exit_code": result.returncode}
    finally:
        os.unlink(tmp_path)