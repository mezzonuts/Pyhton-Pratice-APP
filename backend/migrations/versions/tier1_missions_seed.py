"""Seed Tier 1 missions

Revision ID: 20261117_002
Revises: 20261117_001
Create Date: 2026-11-17 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20261117_002"
down_revision = "20261117_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    missions = []

    # JSON parsing (4 missions) - difficulty_rating 1100-1112
    json_missions = [
        (1, "JSON Parsing Basics", "build_feature", '{"a": 1}'),
        (2, "JSON Validation", "fix_bug", '{"a": 1}'),
        (3, "Nested JSON Extraction", "refactor", '{"a": 1}'),
        (4, "JSON Data Transformation", "build_feature", '{"a": 1}'),
    ]
    for i, (id, title, mode, data) in enumerate(json_missions):
        missions.append({
            "id": id + 100,  # IDs start at 101
            "title": title,
            "tier": 1,
            "mode": mode,
            "ticket_markdown": f"TKT-2026-T1-{id+1}\nParse and transform JSON data.",
            "starter_code": "def process_json(data):\n    pass\n",
            "solution_code": "import json\n\ndef process_json(data):\n    return json.loads(data)",
            "test_file": "tests/test_json.py",
            "expected_interface": "process_json(data: dict) -> dict",
            "time_limit_minutes": 10,
            "xp_reward": 100,
            "difficulty_rating": 1100 + i * 3,
            "tags": '["json", "data_wrangling"]',
            "is_boss_fight": False,
        })

    # CSV parsing (4 missions) - difficulty_rating 1113-1125
    csv_missions = [
        (5, "CSV Parsing Basics", "build_feature", ""),
        (6, "CSV Filtering", "fix_bug", ""),
        (7, "CSV Aggregation", "refactor", ""),
        (8, "CSV Data Transformation", "build_feature", ""),
    ]
    for i, (id, title, mode, data) in enumerate(csv_missions):
        missions.append({
            "id": id + 100,
            "title": title,
            "tier": 1,
            "mode": mode,
            "ticket_markdown": f"TKT-2026-T1-{id+1}\nParse and transform CSV data.",
            "starter_code": "def process_csv(data):\n    pass\n",
            "solution_code": "import csv\n\ndef process_csv(data):\n    rows = list(csv.reader(data.splitlines()))\n    return rows",
            "test_file": "tests/test_csv.py",
            "expected_interface": "process_csv(data: str) -> list",
            "time_limit_minutes": 10,
            "xp_reward": 100,
            "difficulty_rating": 1113 + i * 3,
            "tags": '["csv", "data_wrangling"]',
            "is_boss_fight": False,
        })

    # Error handling (8 missions: try/except, custom exceptions) - difficulty_rating 1126-1161
    error_missions = [
        (9, "Try-Except Basics", "fix_bug"),
        (10, "Custom Exception Creation", "refactor"),
        (11, "Resource Management", "build_feature"),
        (12, "Error Propagation", "fix_bug"),
        (13, "Input Validation", "refactor"),
        (14, "Error Logging", "build_feature"),
        (15, "Retry Logic", "fix_bug"),
        (16, "Error Aggregation", "refactor"),
    ]
    for i, (id, title, mode) in enumerate(error_missions):
        missions.append({
            "id": id + 100,
            "title": title,
            "tier": 1,
            "mode": mode,
            "ticket_markdown": f"TKT-2026-T1-{id+1}\nHandle errors and exceptions properly.",
            "starter_code": "def risky_function(data):\n    pass\n",
            "solution_code": "def risky_function(data):\n    try:\n        return process(data)\n    except Exception as e:\n        raise ValueError(f\"Error: {e}\")",
            "test_file": "tests/test_error.py",
            "expected_interface": "risky_function(data: str) -> str or ValueError",
            "time_limit_minutes": 10,
            "xp_reward": 100,
            "difficulty_rating": 1126 + i * 5,
            "tags": '["error_handling"]',
            "is_boss_fight": False,
        })

    # Big-O awareness (6 missions: complexity analysis, optimization) - difficulty_rating 1162-1192
    big_o_missions = [
        (17, "Complexity Analysis I", "refactor"),
        (18, "Complexity Analysis II", "build_feature"),
        (19, "Optimization I", "refactor"),
        (20, "Optimization II", "build_feature"),
        (21, "Best Case Selection", "refactor"),
        (22, "Complexity Comparison", "build_feature"),
    ]
    for i, (id, title, mode) in enumerate(big_o_missions):
        missions.append({
            "id": id + 100,
            "title": title,
            "tier": 1,
            "mode": mode,
            "ticket_markdown": f"TKT-2026-T1-{id+1}\nAnalyze and optimize algorithm complexity.",
            "starter_code": "def process(data):\n    pass\n",
            "solution_code": "def process(data):\n    # O(n) optimized version\n    result = []\n    for i in range(len(data)):\n        result.append(data[i])\n    return result",
            "test_file": "tests/test_big_o.py",
            "expected_interface": "process(data: list) -> list",
            "time_limit_minutes": 10,
            "xp_reward": 100,
            "difficulty_rating": 1162 + i * 5,
            "tags": '["big_o"]',
            "is_boss_fight": False,
        })

    # Mixed mode (4 missions: mixed fix_build_refactor) - difficulty_rating 1193-1204
    mixed_missions = [
        (23, "Mixed Fix-Build-Refactor I", "fix_bug"),
        (24, "Mixed Fix-Build-Refactor II", "build_feature"),
        (25, "Mixed Fix-Build-Refactor III", "refactor"),
        (26, "Mixed Fix-Build-Refactor IV", "fix_bug"),
    ]
    for i, (id, title, mode) in enumerate(mixed_missions):
        missions.append({
            "id": id + 100,
            "title": title,
            "tier": 1,
            "mode": mode,
            "ticket_markdown": f"TKT-2026-T1-{id+1}\nMixed fix/build/refactor mission.",
            "starter_code": "def process(data):\n    pass\n",
            "solution_code": "def process(data):\n    # Mixed fix/build/refactor logic\n    return None",
            "test_file": "tests/test_mixed.py",
            "expected_interface": "process(data: str) -> None",
            "time_limit_minutes": 10,
            "xp_reward": 100,
            "difficulty_rating": 1193 + i * 3,
            "tags": '["fix_bug", "build_feature", "refactor"]',
            "is_boss_fight": False,
        })

    # Insert missions into database
    connection = op.get_bind()
    for m in missions:
        connection.execute(
            sa.insert("mission_templates"),
            {
                "id": m["id"],
                "title": m["title"],
                "tier": m["tier"],
                "mode": m["mode"],
                "difficulty_type": "data_wrangling",  # default, will be overridden by actual value
                "prerequisite_tier": 0,
                "ticket_markdown": m["ticket_markdown"],
                "starter_code": m["starter_code"],
                "solution_code": m["solution_code"],
                "test_file": m["test_file"],
                "expected_interface": m["expected_interface"],
                "time_limit_minutes": m["time_limit_minutes"],
                "xp_reward": m["xp_reward"],
                "difficulty_rating": m["difficulty_rating"],
                "tags": m["tags"],
                "is_boss_fight": m["is_boss_fight"],
                "created_at": sa.text("now()"),
            }
        )
    connection.commit()
    print(f"Seeded {len(missions)} Tier 1 missions successfully!")


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM mission_templates WHERE tier = 1"))
    connection.commit()
    print("Removed Tier 1 missions.")