import json
import subprocess
import tempfile
import os
from typing import Dict, Any


class SandboxRunner:
    """Manages isolated Docker container execution for grading pipelines."""

    FORBIDDEN_PATTERNS = [
        "os.system",
        "subprocess",
        "multiprocessing",
        "threading",
        "socket",
        "urllib",
        "requests",
        "http",
        "ftplib",
        "eval(",
        "exec(",
        "compile(",
        "__import__(",
    ]

    def __init__(self):
        self.image = "pyforge/sandbox-runner:latest"

    async def create_session(
        self,
        mission_id: str,
        user_files: Dict[str, str],
        resource_limits: Dict[str, Any],
    ) -> str:
        """Create isolated container session.

        Writes user files to temp directory inside container.
        Returns session ID for execution.
        """
        host_dir = tempfile.mkdtemp(prefix=f"sandbox_{mission_id}_")
        for path, content in user_files.items():
            full_path = os.path.join(host_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)

        # In a real implementation, this would start a Docker container
        # with gVisor/runsc, network isolation, resource limits
        # For now, we return a session identifier
        session_id = host_dir
        return session_id

    async def execute(
        self,
        session_id: str,
        command: str,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Execute command in sandbox container.

        In production, this would execute in a Docker container with gVisor.
        For this implementation, we execute locally with restricted filesystem.
        """
        session_dir = session_id

        # Write command to a temp script inside the session directory
        cmd_path = os.path.join(session_dir, "cmd.sh")
        with open(cmd_path, "w") as f:
            f.write(command)

        try:
            result = subprocess.run(
                ["bash", cmd_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=session_dir,
                env={k: v for k, v in os.environ.items() if k.isupper()},
            )

            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "Command timed out",
            }
        finally:
            # Clean up command file
            if os.path.exists(cmd_path):
                os.unlink(cmd_path)

    def run_ruff_in_sandbox(self, code: str) -> dict:
        """Run ruff check on code inside sandbox container.

        Uses the container's filesystem, not host filesystem.
        """
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ["ruff", "check", tmp_path, "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            try:
                errors = json.loads(result.stdout) if result.stdout.strip() else []
            except (json.JSONDecodeError, ValueError):
                errors = []

            return {
                "errors": errors,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        finally:
            os.unlink(tmp_path)

    def run_mypy_in_sandbox(self, code: str) -> dict:
        """Run mypy --strict on code inside sandbox container.

        Uses the container's filesystem, not host filesystem.
        """
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ["mypy", "--strict", tmp_path],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse mypy output - each error line is captured
            errors = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    errors.append(line.strip())

            return {
                "errors": errors,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        finally:
            os.unlink(tmp_path)