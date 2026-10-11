import os
import sqlite3
from config import DB_PATH

def _connect():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL DEFAULT '',
                full_name TEXT NOT NULL DEFAULT '',
                first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def register_user(user_id: int, username: str, full_name: str):
    with _connect() as conn:
        conn.execute(
            """INSERT INTO users(user_id, username, full_name)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
               username=excluded.username, full_name=excluded.full_name""",
            (user_id, username, full_name),
        )

def record_download(user_id: int, media_type: str):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO downloads(user_id, media_type) VALUES (?, ?)",
            (user_id, media_type),
        )

def get_stats():
    with _connect() as conn:
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        videos = conn.execute(
            "SELECT COUNT(*) FROM downloads WHERE media_type='video'"
        ).fetchone()[0]
        audios = conn.execute(
            "SELECT COUNT(*) FROM downloads WHERE media_type='audio'"
        ).fetchone()[0]
    return {
        "users": users,
        "videos": videos,
        "audios": audios,
        "total": videos + audios,
    }
