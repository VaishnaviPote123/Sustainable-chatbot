import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")


def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            total_carbon_saved REAL DEFAULT 0,
            streak INTEGER DEFAULT 0,
            last_challenge_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Daily challenges table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            carbon_value INTEGER,
            category TEXT,
            difficulty TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # User challenge completion table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(challenge_id) REFERENCES challenges(id)
        )
    """
    )

    # Carbon savings log table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS carbon_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            carbon_saved REAL NOT NULL,
            activity TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """
    )

    # Habit reminders table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            habit TEXT NOT NULL,
            frequency TEXT,
            enabled INTEGER DEFAULT 1,
            last_reminded TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """
    )

    # Daily challenge table (stores the challenge of the day)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS challenge_of_day (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            challenge_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


def get_user(username):
    """Get user by username"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def create_user(username, email=""):
    """Create new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)", (username, email)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_leaderboard(limit=10):
    """Get top users by carbon saved"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, total_carbon_saved, streak FROM users ORDER BY total_carbon_saved DESC LIMIT ?",
        (limit,),
    )
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def log_carbon(user_id, carbon_saved, activity):
    """Log carbon saved"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO carbon_log (user_id, carbon_saved, activity) VALUES (?, ?, ?)",
        (user_id, carbon_saved, activity),
    )
    # Update user total
    cursor.execute(
        "UPDATE users SET total_carbon_saved = total_carbon_saved + ? WHERE id = ?",
        (carbon_saved, user_id),
    )
    conn.commit()
    conn.close()


def set_challenge_of_day(challenge_id):
    """Set the challenge of the day"""
    from datetime import date

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = str(date.today())
    cursor.execute(
        "INSERT OR REPLACE INTO challenge_of_day (date, challenge_id) VALUES (?, ?)",
        (today, challenge_id),
    )
    conn.commit()
    conn.close()


def get_challenge_of_day():
    """Get today's challenge for all users"""
    from datetime import date

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = str(date.today())
    cursor.execute("SELECT challenge_id FROM challenge_of_day WHERE date = ?", (today,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def add_reminder(user_id, habit, frequency):
    """Add a reminder for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reminders (user_id, habit, frequency, enabled) VALUES (?, ?, ?, 1)",
        (user_id, habit, frequency),
    )
    conn.commit()
    conn.close()


def get_user_reminders(user_id):
    """Get all reminders for a user"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reminders WHERE user_id = ? AND enabled = 1", (user_id,)
    )
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def toggle_reminder(reminder_id, enabled):
    """Enable/disable a reminder"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reminders SET enabled = ? WHERE id = ?", (enabled, reminder_id)
    )
    conn.commit()
    conn.close()


# Initialize database on import
init_db()
