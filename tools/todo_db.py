"""
Todo/task storage — per-user isolation via user_id.
All queries are scoped to the requesting user.
"""
import os
import logging
from tools.db_utils import get_db_connection, execute_query, execute_script, IS_POSTGRES

logger  = logging.getLogger(__name__)

def init_db():
    sqlite_schema = """
        CREATE TABLE IF NOT EXISTS todos (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            task      TEXT    NOT NULL,
            due_date  TEXT,
            priority  TEXT    DEFAULT 'normal',
            done      INTEGER DEFAULT 0,
            created   TEXT    DEFAULT (datetime('now','localtime')),
            user_id   INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_todos_user ON todos(user_id, done, due_date);
    """
    
    postgres_schema = """
        CREATE TABLE IF NOT EXISTS todos (
            id        SERIAL PRIMARY KEY,
            task      TEXT    NOT NULL,
            due_date  TEXT,
            priority  TEXT    DEFAULT 'normal',
            done      INTEGER DEFAULT 0,
            created   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id   INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_todos_user ON todos(user_id, done, due_date);
    """

    with get_db_connection("aria_todos.db") as conn:
        execute_script(conn, postgres_schema if IS_POSTGRES else sqlite_schema)


def add_task(task: str, user_id: int = 0, due_date: str = None, priority: str = "normal") -> int:
    with get_db_connection("aria_todos.db") as conn:
        cursor = execute_query(
            conn,
            "INSERT INTO todos (user_id, task, due_date, priority) VALUES (?, ?, ?, ?) RETURNING id" if IS_POSTGRES else "INSERT INTO todos (user_id, task, due_date, priority) VALUES (?, ?, ?, ?)",
            (user_id, task, due_date, priority)
        )
        if IS_POSTGRES:
            return cursor.fetchone()["id"]
        else:
            return cursor.lastrowid


def get_tasks(filter: str = "pending", user_id: int = 0) -> list:
    with get_db_connection("aria_todos.db") as conn:
        if filter == "done":
            rows = execute_query(
                conn,
                "SELECT * FROM todos WHERE user_id=? AND done=1 ORDER BY created DESC LIMIT 10",
                (user_id,)
            ).fetchall()
        elif filter == "all":
            rows = execute_query(
                conn,
                "SELECT * FROM todos WHERE user_id=? ORDER BY done ASC, created DESC",
                (user_id,)
            ).fetchall()
        else:  # pending
            rows = execute_query(
                conn,
                "SELECT * FROM todos WHERE user_id=? AND done=0 ORDER BY priority DESC, due_date ASC",
                (user_id,)
            ).fetchall()
        return [dict(r) for r in rows]


def complete_task(task_id: int, user_id: int = 0) -> bool:
    """Mark a task done — only if it belongs to this user."""
    with get_db_connection("aria_todos.db") as conn:
        cursor = execute_query(
            conn,
            "UPDATE todos SET done=1 WHERE id=? AND user_id=?",
            (task_id, user_id)
        )
        return cursor.rowcount > 0


def delete_task(task_id: int, user_id: int = 0) -> bool:
    """Delete a task — only if it belongs to this user."""
    with get_db_connection("aria_todos.db") as conn:
        cursor = execute_query(
            conn,
            "DELETE FROM todos WHERE id=? AND user_id=?",
            (task_id, user_id)
        )
        return cursor.rowcount > 0


# Auto-create table on import
init_db()
