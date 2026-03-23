import sqlite3
from datetime import datetime, timedelta
import bcrypt

def get_db_connection():
    conn = sqlite3.connect('habits.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS habits (
            habit_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            periodicity TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE TABLE IF NOT EXISTS completions (
            completion_id INTEGER PRIMARY KEY,
            habit_id INTEGER NOT NULL,
            completed_at TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(habit_id)
        );
        CREATE TABLE IF NOT EXISTS streaks (
            streak_id INTEGER PRIMARY KEY,
            habit_id INTEGER NOT NULL,
            streak_count INTEGER DEFAULT 0,
            last_completed_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(habit_id)
        );
    ''')
    conn.commit()
    conn.close()

def preload_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Create test user
    hashed = bcrypt.hashpw(b"password", bcrypt.gensalt())
    cursor.execute("INSERT INTO users (email, username, password, created_at) VALUES (?, ?, ?, ?)",
                   ("test@example.com", "test", hashed, datetime.now().isoformat()))
    user_id = cursor.lastrowid
    conn.commit()

    # 5 predefined habits (3 daily + 2 weekly)
    habits = [
        ("Drink water", "8 glasses daily", "daily"),
        ("Exercise", "30 minutes", "daily"),
        ("Read book", "20 pages", "daily"),
        ("Clean house", "Full cleaning", "weekly"),
        ("Grocery shopping", "Weekly shopping", "weekly")
    ]
    habit_ids = []
    for name, desc, period in habits:
        cursor.execute("INSERT INTO habits (user_id, name, description, periodicity, created_at, is_active) VALUES (?, ?, ?, ?, ?, 1)",
                       (user_id, name, desc, period, datetime.now().isoformat()))
        habit_ids.append(cursor.lastrowid)
    conn.commit()

    # 4 weeks of example data (with some breaks for testing streaks)
    start = datetime.now() - timedelta(weeks=4)
    for i in range(28):
        date = start + timedelta(days=i)
        for j, hid in enumerate(habit_ids):
            if j < 3:  # daily habits - skip every Wednesday
                if date.weekday() != 2:
                    cursor.execute("INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
                                   (hid, date.isoformat()))
            else:  # weekly - complete only on Sunday, skip week 2
                if date.weekday() == 6 and (i // 7) != 2:
                    cursor.execute("INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
                                   (hid, date.isoformat()))
    conn.commit()
    conn.close()