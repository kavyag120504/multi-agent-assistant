"""
Persistent conversation memory per user.
Stores full chat history in SQLite/PostgreSQL so it survives page refreshes and restarts.
"""
import os
import logging
from datetime import datetime
from tools.db_utils import get_db_connection, execute_query, execute_script, IS_POSTGRES

logger  = logging.getLogger(__name__)

def init_memory_table():
    sqlite_schema = """
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
    """
    
    postgres_schema = """
        CREATE TABLE IF NOT EXISTS conversation_history (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            role       TEXT    NOT NULL CHECK(role IN ('user','assistant')),
            content    TEXT    NOT NULL,
            intent     TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_history_user
            ON conversation_history(user_id, created_at);
    """
    
    with get_db_connection("aria_users.db") as conn:
        execute_script(conn, postgres_schema if IS_POSTGRES else sqlite_schema)


def save_message(user_id: int, role: str, content: str, intent: str = None):
    """Persist a single message to the DB."""
    try:
        with get_db_connection("aria_users.db") as conn:
            execute_query(
                conn,
                """INSERT INTO conversation_history
                   (user_id, role, content, intent)
                   VALUES (?, ?, ?, ?)""",
                (user_id, role, content, intent)
            )
    except Exception as e:
        logger.error(f"Failed to save message for user {user_id}: {e}")


def load_history(user_id: int, limit: int = 50) -> list[dict]:
    """
    Load last `limit` messages for a user.
    Returns list of dicts with keys: role, content, intent, created_at
    """
    try:
        with get_db_connection("aria_users.db") as conn:
            cursor = execute_query(
                conn,
                """
                SELECT role, content, intent, created_at
                FROM conversation_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """, 
                (user_id, limit)
            )
            rows = cursor.fetchall()
            
        # Format created_at to string if it's datetime (for Postgres)
        formatted_rows = []
        for r in rows:
            row_dict = dict(r)
            if IS_POSTGRES and isinstance(row_dict.get('created_at'), datetime):
                row_dict['created_at'] = row_dict['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            formatted_rows.append(row_dict)
            
        # Reverse so oldest first
        return list(reversed(formatted_rows))
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
    with get_db_connection("aria_users.db") as conn:
        execute_query(conn, "DELETE FROM conversation_history WHERE user_id = ?", (user_id,))
    logger.info(f"Cleared history for user {user_id}")


def get_message_count(user_id: int) -> int:
    """Return total message count for a user."""
    with get_db_connection("aria_users.db") as conn:
        cursor = execute_query(conn, "SELECT COUNT(*) as cnt FROM conversation_history WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
    return row["cnt"] if row else 0


# Auto-init on import
init_memory_table()
