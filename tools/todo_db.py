"""
Todo/task storage — per-user isolation via user_id.
All queries are scoped to the requesting user.
"""
import sqlite3
import os
import logging

logger  = logging.getLogger(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "aria_todos.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with _get_conn() as conn:
        # ── Step 1: Create table without the index ────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                task      TEXT    NOT NULL,
                due_date  TEXT,
                priority  TEXT    DEFAULT 'normal',
                done      INTEGER DEFAULT 0,
                created   TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()

        # ── Step 2: Migrate — add user_id if missing ──────────────────────────
        existing_cols = [
            row[1] for row in conn.execute("PRAGMA table_info(todos)").fetchall()
        ]
        if "user_id" not in existing_cols:
            conn.execute(
                "ALTER TABLE todos ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0"
            )
            conn.commit()

        # ── Step 3: Create index now that user_id is guaranteed to exist ──────
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_todos_user
            ON todos(user_id, done, due_date)
        """)
        conn.commit()


def add_task(task: str, user_id: int = 0,
             due_date: str = None, priority: str = "normal") -> int:
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO todos (user_id, task, due_date, priority) VALUES (?, ?, ?, ?)",
            (user_id, task, due_date, priority)
        )
        conn.commit()
        return cur.lastrowid


def get_tasks(filter: str = "pending", user_id: int = 0) -> list:
    with _get_conn() as conn:
        if filter == "done":
            rows = conn.execute(
                "SELECT * FROM todos WHERE user_id=? AND done=1 "
                "ORDER BY created DESC LIMIT 10",
                (user_id,)
            ).fetchall()
        elif filter == "all":
            rows = conn.execute(
                "SELECT * FROM todos WHERE user_id=? "
                "ORDER BY done ASC, created DESC",
                (user_id,)
            ).fetchall()
        else:  # pending
            rows = conn.execute(
                "SELECT * FROM todos WHERE user_id=? AND done=0 "
                "ORDER BY priority DESC, due_date ASC",
                (user_id,)
            ).fetchall()
        return [dict(r) for r in rows]


def complete_task(task_id: int, user_id: int = 0) -> bool:
    """Mark a task done — only if it belongs to this user."""
    with _get_conn() as conn:
        conn.execute(
            "UPDATE todos SET done=1 WHERE id=? AND user_id=?",
            (task_id, user_id)
        )
        conn.commit()
        return conn.total_changes > 0


def delete_task(task_id: int, user_id: int = 0) -> bool:
    """Delete a task — only if it belongs to this user."""
    with _get_conn() as conn:
        conn.execute(
            "DELETE FROM todos WHERE id=? AND user_id=?",
            (task_id, user_id)
        )
        conn.commit()
        return conn.total_changes > 0


# Auto-create table on import
init_db()
