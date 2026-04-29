"""
Persistent conversation memory per user.
Stores full chat history in SQLite so it survives page refreshes and restarts.
"""
import sqlite3
import os
import logging
from datetime import datetime

logger  = logging.getLogger(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "aria_users.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_memory_table():
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                role       TEXT    NOT NULL CHECK(role IN ('user','assistant')),
                content    TEXT    NOT NULL,
                intent     TEXT,
                created_at TEXT    DEFAULT (datetime('now','localtime'))
            );

            CREATE INDEX IF NOT EXISTS idx_history_user
                ON conversation_history(user_id, created_at);
        """)
        conn.commit()


def save_message(user_id: int, role: str, content: str, intent: str = None):
    """Persist a single message to the DB."""
    try:
        with _get_conn() as conn:
            conn.execute(
                """INSERT INTO conversation_history
                   (user_id, role, content, intent)
                   VALUES (?, ?, ?, ?)""",
                (user_id, role, content, intent)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to save message for user {user_id}: {e}")


def load_history(user_id: int, limit: int = 50) -> list[dict]:
    """
    Load last `limit` messages for a user.
    Returns list of dicts with keys: role, content, intent, created_at
    """
    try:
        with _get_conn() as conn:
            rows = conn.execute("""
                SELECT role, content, intent, created_at
                FROM conversation_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()
        # Reverse so oldest first
        return [dict(r) for r in reversed(rows)]
    except Exception as e:
        logger.error(f"Failed to load history for user {user_id}: {e}")
        return []


def get_context_text(user_id: int, n: int = 6) -> str:
    """
    Return last n messages as plain text for agent context injection.
    """
    messages = load_history(user_id, limit=n)
    lines = []
    for msg in messages:
        prefix = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{prefix}: {msg['content']}")
    return "\n".join(lines)


def clear_history(user_id: int):
    """Delete all conversation history for a user."""
    with _get_conn() as conn:
        conn.execute(
            "DELETE FROM conversation_history WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
    logger.info(f"Cleared history for user {user_id}")


def get_message_count(user_id: int) -> int:
    """Return total message count for a user."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM conversation_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()
    return row["cnt"] if row else 0


# Auto-init on import
init_memory_table()
