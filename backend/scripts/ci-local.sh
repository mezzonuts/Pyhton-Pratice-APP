#!/usr/bin/env bash
set -euo pipefail

echo "=== Ruff check ==="
ruff check backend/app

echo "=== Ruff format check ==="
ruff format --check backend/app

echo "=== MyPy strict ==="
mypy --strict backend/app

echo "=== Pytest with coverage ==="
pytest --cov=app --cov-fail-under=80 backend/tests

echo "=== Bandit security scan ==="
bandit -r backend/app -ll