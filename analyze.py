from db import get_db_connection
from datetime import datetime, timedelta

def list_all_habits(user_id):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM habits WHERE user_id = ? AND is_active = 1", (user_id,)).fetchall()
    conn.close()
    return rows

def list_habits_by_periodicity(user_id, periodicity):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM habits WHERE user_id = ? AND periodicity = ? AND is_active = 1",
                        (user_id, periodicity)).fetchall()
    conn.close()
    return rows

def longest_streak_for_habit(habit_id):
    conn = get_db_connection()
    period = conn.execute("SELECT periodicity FROM habits WHERE habit_id = ?", (habit_id,)).fetchone()["periodicity"]
    completions = [row["completed_at"] for row in conn.execute(
        "SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at", (habit_id,)).fetchall()]
    conn.close()

    if not completions:
        return 0
    days = 1 if period == "daily" else 7
    dates = [datetime.fromisoformat(c).date() for c in completions]
    periods = sorted(set(d - timedelta(days=d.weekday() % days) for d in dates))  # normalize to period start
    max_streak = current = 1
    for i in range(1, len(periods)):
        if (periods[i] - periods[i-1]).days == days:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 1
    return max_streak

def longest_global_streak(user_id):
    conn = get_db_connection()
    habit_ids = [row["habit_id"] for row in conn.execute(
        "SELECT habit_id FROM habits WHERE user_id = ? AND is_active = 1", (user_id,)).fetchall()]
    conn.close()
    return max((longest_streak_for_habit(hid) for hid in habit_ids), default=0)

def inactive_habits(user_id):
    six_months = (datetime.now() - timedelta(days=180)).isoformat()
    conn = get_db_connection()
    rows = conn.execute("""SELECT * FROM habits 
                           WHERE user_id = ? AND is_active = 1 
                           AND habit_id NOT IN (SELECT habit_id FROM completions WHERE completed_at > ?)""",
                        (user_id, six_months)).fetchall()
    conn.close()
    return rows