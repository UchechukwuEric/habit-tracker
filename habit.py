from db import get_db_connection
from datetime import datetime
import bcrypt

class User:
    def __init__(self, user_id, email, username, password, created_at):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.password = password
        self.created_at = created_at

    @classmethod
    def register_user(cls, email, username, password):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, username, password, created_at) VALUES (?, ?, ?, ?)",
                       (email, username, hashed, datetime.now().isoformat()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return cls(user_id, email, username, hashed, datetime.now().isoformat())

class Habit:
    @classmethod
    def create_habit(cls, user_id, name, description, periodicity):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO habits (user_id, name, description, periodicity, created_at, is_active) VALUES (?, ?, ?, ?, ?, 1)",
                       (user_id, name, description, periodicity, datetime.now().isoformat()))
        habit_id = cursor.lastrowid
        cursor.execute("INSERT INTO streaks (habit_id, streak_count, created_at) VALUES (?, 0, ?)",
                       (habit_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return habit_id

    @classmethod
    def deactivate_habit(cls, habit_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE habits SET is_active = 0 WHERE habit_id = ?", (habit_id,))
        conn.commit()
        conn.close()