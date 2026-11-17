import sqlite3

conn = sqlite3.connect("test.db")

# Check mission_templates count
cursor = conn.execute("SELECT COUNT(*) FROM mission_templates")
count = cursor.fetchone()[0]
print(f"mission_templates: {count} rows")

# Check first few missions
cursor = conn.execute("SELECT id, title, tier, mode FROM mission_templates LIMIT 5")
for row in cursor:
    print(f"  {row}")

# Check user_mission_states
cursor = conn.execute("SELECT COUNT(*) FROM user_mission_states")
count = cursor.fetchone()[0]
print(f"user_mission_states: {count} rows")

# Check users
cursor = conn.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"users: {count} rows")

# Check unique constraint - try to insert duplicate
try:
    conn.execute(
        "INSERT INTO user_mission_states (user_id, mission_date, status) VALUES (1, '2026-01-15', 'not_started')"
    )
    conn.commit()
    # Try again - should fail
    conn.execute(
        "INSERT INTO user_mission_states (user_id, mission_date, status) VALUES (1, '2026-01-15', 'not_started')"
    )
    conn.commit()
    print("Unique constraint: FAILED (duplicate inserted)")
except Exception as e:
    print(f"Unique constraint: OK (duplicate rejected: {e})")

conn.close()
print("\nAll verification complete!")