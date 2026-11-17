import os, sys, sqlite3
sys.path.insert(0, r"D:\Project\Pyhton Pratice APP\backend")

# Direct database seeding without importing app models
engine = sqlite3.connect("test.db")
cursor = engine.cursor()

# Create tables if not exist (matching the SQLAlchemy models)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    tier INTEGER DEFAULT 0,
    elo_rating INTEGER DEFAULT 1000,
    streak_days INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    freeze_shields INTEGER DEFAULT 0,
    total_xp INTEGER DEFAULT 0,
    skill_radar TEXT DEFAULT '{}',
    ai_config TEXT DEFAULT '{}',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT (datetime('now')),
    last_active TIMESTAMP DEFAULT (datetime('now'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mission_templates (
    id INTEGER PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    tier INTEGER NOT NULL,
    mode TEXT NOT NULL,
    ticket_markdown TEXT NOT NULL,
    starter_code TEXT NOT NULL,
    solution_code TEXT NOT NULL,
    test_file TEXT NOT NULL,
    expected_interface TEXT NOT NULL,
    time_limit_minutes INTEGER NOT NULL,
    xp_reward INTEGER NOT NULL,
    difficulty_rating INTEGER NOT NULL,
    tags JSON NOT NULL DEFAULT '[]',
    is_boss_fight INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT (datetime('now'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_mission_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mission_id INTEGER NOT NULL,
    mission_date TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    grade TEXT,
    score INTEGER,
    xp_earned INTEGER NOT NULL DEFAULT 0,
    elo_change INTEGER,
    code_snapshot TEXT,
    started_at TIMESTAMP,
    submitted_at TIMESTAMP,
    completed_at TIMESTAMP,
    UNIQUE(user_id, mission_date)
)
""")

# Insert 14 Tier 0 missions
missions = [
    (1, "Variables and Types", 0, "fix_bug",
     "TKT-2026-001\nFix the type errors in the given code.\nVariables are properly typed\nString concatenation works correctly\nInteger arithmetic works correct",
     "def process_data(name, age, score):\n    result = age + score\n    return f\"{name}: {result}\"",
     "def process_data(name, age, score):\n    total = int(age) + int(score)\n    return f\"{name}: {total}\"",
     "tests/test_process.py", "process_data(name: str, age: str, score: str) -> str",
     5, 100, 1000, '["basic", "logic", "variable", "type"]', 0),
    (2, "String Operations", 0, "build_feature",
     "TKT-2026-002\nImplement string manipulation functions.\nString reversal works\nCase conversion works\nString length calculation works\nSubstring extraction works",
     "def reverse_string(s):\n    pass\n\ndef capitalize_first(s):\n    pass",
     "def reverse_string(s):\n    return s[::-1]\n\ndef capitalize_first(s):\n    if not s:\n        return s\n    return s[0].upper() + s[1:]",
     "tests/test_string.py", "reverse_string(s: str) -> str, capitalize_first(s: str) -> str",
     5, 100, 1000, '["basic", "string", "function"]', 0),
    (3, "If-Else branching", 0, "fix_bug",
     "TKT-2026-003\nFix the logical errors in the branching code.\nAll edge cases handled\nCorrect boolean logic\nNo unreachable code",
     "def check_number(n):\n    if n > 0:\n        return \"positive\"\n    elif n == 0:\n        return \"zero\"\n    else:\n        return \"negative\"\n\nresult = check_number(-5)\nprint(result)",
     "def check_number(n):\n    if n > 0:\n        return \"positive\"\n    elif n == 0:\n        return \"zero\"\n    else:\n        return \"negative\"",
     "tests/test_check.py", "check_number(n: int) -> str",
     5, 100, 1000, '["basic", "logic", "branching"]', 0),
    (4, "For Loops", 0, "build_feature",
     "TKT-2026-004\nImplement a loop to calculate sum of numbers.\nSum of 1 to n calculated correctly\nHandles n=0 case\nUses for loop construct",
     "def sum_to_n(n):\n    pass\n\nresult = sum_to_n(5)\nprint(result)",
     "def sum_to_n(n):\n    total = 0\n    for i in range(1, n + 1):\n        total += i\n    return total",
     "tests/test_sum.py", "sum_to_n(n: int) -> int",
     5, 100, 1000, '["basic", "loop", "function"]', 0),
    (5, "While Loops", 0, "fix_bug",
     "TKT-2026-005\nFix the infinite loop and off-by-one errors.\nLoop terminates correctly\nCounter increments properly\nNo infinite loop",
     "def count_down(n):\n    while n > 0:\n        print(n)\n        n = n - 1\n    return \"done\"\n\nresult = count_down(3)\nprint(result)",
     "def count_down(n):\n    while n > 0:\n        print(n)\n        n = n - 1\n    return \"done\"",
     "tests/test_count.py", "count_down(n: int) -> str",
     5, 100, 1000, '["basic", "loop"]', 0),
    (6, "Functions Basics", 0, "build_feature",
     "TKT-2026-006\nCreate a function that computes area of rectangle.\nFunction accepts two parameters\nReturns correct area\nHandles zero dimensions",
     "def area_rectangle(length, width):\n    pass\n\nresult = area_rectangle(3, 4)\nprint(result)",
     "def area_rectangle(length, width):\n    return length * width",
     "tests/test_area.py", "area_rectangle(length: float, width: float) -> float",
     5, 100, 1000, '["basic", "function"]', 0),
    (7, "List Operations", 0, "fix_bug",
     "TKT-2026-007\nFix the list index out of range errors.\nNo IndexError\nList operations work correctly\nEmpty list handled",
     "def get_first_three(lst):\n    return [lst[0], lst[1], lst[2]\n\nresult = get_first_three([1, 2, 3, 4])\nprint(result)",
     "def get_first_three(lst):\n    return lst[:3]",
     "tests/test_list.py", "get_first_three(lst: list) -> list",
     5, 100, 1000, '["basic", "list"]', 0),
    (8, "Dict Operations", 0, "build_feature",
     "TKT-2026-008\nImplement a function to count character frequencies.\nReturns dict with character counts\nCase-insensitive counting\nHandles empty string",
     "def char_frequency(s):\n    pass\n\nresult = char_frequency(\"hello\")\nprint(result)",
     "def char_frequency(s):\n    freq = {}\n    for c in s.lower():\n        freq[c] = freq.get(c, 0) + 1\n    return freq",
     "tests/test_freq.py", "char_frequency(s: str) -> dict",
     5, 100, 1000, '["basic", "dict"]', 0),
    (9, "Error Handling", 0, "fix_bug",
     "TKT-2026-009\nFix the missing try-except blocks.\nNo unhandled exceptions\nProper error messages\nProgram doesnt crash on invalid input",
     "def safe_divide(a, b):\n    return a / b\n\nresult = safe_divide(10, 0)\nprint(result)",
     "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return \"Cannot divide by zero\"",
     "tests/test_divide.py", "safe_divide(a: float, b: float) -> float or str",
     5, 100, 1000, '["basic", "error_handling"]', 0),
    (10, "Modules Import", 0, "build_feature",
     "TKT-2026-010\nImport math module and use sqrt function.\nmath module imported\nsqrt function used correctly\nNo import errors",
     "def calculate_hypoteneuse(a, b):\n    pass\n\nresult = calculate_hypoteneuse(3, 4)\nprint(result)",
     "import math\ndef calculate_hypoteneuse(a, b):\n    return math.sqrt(a**2 + b**2)",
     "tests/test_hypot.py", "calculate_hypoteneuse(a: float, b: float) -> float",
     5, 100, 1000, '["basic"]', 0),
    (11, "Comparison Operators", 0, "fix_bug",
     "TKT-2026-011\nFix the comparison logic errors.\nCorrect boolean results\nEdge cases handled\nNo logic errors",
     "def are_equal(a, b):\n    if a = b:\n        return True\n    return False\n\nresult = are_equal(5, 5)\nprint(result)",
     "def are_equal(a, b):\n    if a == b:\n        return True\n    return False",
     "tests/test_equal.py", "are_equal(a: int, b: int) -> bool",
     5, 100, 1000, '["basic", "logic"]', 0),
    (12, "Boolean Logic", 0, "build_feature",
     "TKT-2026-012\nImplement AND/OR/NOT operations.\nAll boolean operations work\nTruthy/falsy handling\nNo syntax errors",
     "def boolean_and(a, b):\n    pass\n\ndef boolean_or(a, b):\n    pass\n\nresult1 = boolean_and(True, False)\nresult2 = boolean_or(True, False)\nprint(result1, result2)",
     "def boolean_and(a, b):\n    return a and b\n\ndef boolean_or(a, b):\n    return a or b",
     "tests/test_boolean.py", "boolean_and(a, b) -> bool, boolean_or(a, b) -> bool",
     5, 100, 1000, '["basic", "logic"]', 0),
    (13, "Nested Loops", 0, "fix_bug",
     "TKT-2026-013\nFix the nested loop variable scoping bugs.\nInner loop variable independent\nCorrect iteration counts\nNo variable shadowing issues",
     "def print_pattern(n):\n    for i in range(n):\n        for j in range(i):\n            print(\"*\", end=\"\")\n        print()\n\nprint_pattern(3)",
     "def print_pattern(n):\n    for i in range(n):\n        for j in range(i + 1):\n            print(\"*\", end=\"\")\n        print()",
     "tests/test_pattern.py", "print_pattern(n: int) -> None",
     5, 100, 1000, '["basic", "loop"]', 0),
    (14, "Basic I/O", 0, "build_feature",
     "TKT-2026-014\nRead input and print formatted output.\nReads user input correctly\nOutput formatted as specified\nNo runtime errors",
     "def get_user_input():\n    pass\n\nname = get_user_input()\nprint(f\"Hello, {name}!\")",
     "def get_user_input():\n    return input()\n\nname = get_user_input()\nprint(f\"Hello, {name}!\")",
     "tests/test_io.py", "get_user_input() -> str",
     5, 100, 1000, '["basic"]', 0),
]

for m in missions:
    cursor.execute(
        "INSERT OR IGNORE INTO mission_templates (id, title, tier, mode, ticket_markdown, starter_code, solution_code, test_file, expected_interface, time_limit_minutes, xp_reward, difficulty_rating, tags, is_boss_fight) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        m
    )

engine.commit()
engine.close()
print("14 Tier 0 missions seeded successfully!")