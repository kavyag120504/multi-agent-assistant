import logging
from tools.db_utils import get_db_connection, execute_query, execute_script, IS_POSTGRES

logger = logging.getLogger(__name__)

def init_db():
    sqlite_schema = """
        CREATE TABLE IF NOT EXISTS workflows (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            title        TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            schedule     TEXT,
            condition    TEXT,
            action       TEXT NOT NULL,
            enabled      INTEGER DEFAULT 1,
            created_at   TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_workflows_user ON workflows(user_id);
    """
    
    postgres_schema = """
        CREATE TABLE IF NOT EXISTS workflows (
            id           SERIAL PRIMARY KEY,
            user_id      INTEGER NOT NULL,
            title        TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            schedule     TEXT,
            condition    TEXT,
            action       TEXT NOT NULL,
            enabled      INTEGER DEFAULT 1,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_workflows_user ON workflows(user_id);
    """

    with get_db_connection("aria_workflows.db") as conn:
        execute_script(conn, postgres_schema if IS_POSTGRES else sqlite_schema)

def add_workflow(user_id: int, title: str, trigger_type: str, schedule: str, condition: str, action: str) -> int:
    with get_db_connection("aria_workflows.db") as conn:
        cursor = execute_query(
            conn,
            """INSERT INTO workflows 
               (user_id, title, trigger_type, schedule, condition, action) 
               VALUES (?, ?, ?, ?, ?, ?)""" + (" RETURNING id" if IS_POSTGRES else ""),
            (user_id, title, trigger_type, schedule, condition, action)
        )
        return cursor.fetchone()["id"] if IS_POSTGRES else cursor.lastrowid

def get_workflows(user_id: int) -> list:
    with get_db_connection("aria_workflows.db") as conn:
        cursor = execute_query(
            conn,
            "SELECT * FROM workflows WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return [dict(r) for r in cursor.fetchall()]

def update_workflow_status(workflow_id: int, user_id: int, enabled: bool) -> bool:
    with get_db_connection("aria_workflows.db") as conn:
        cursor = execute_query(
            conn,
            "UPDATE workflows SET enabled = ? WHERE id = ? AND user_id = ?",
            (1 if enabled else 0, workflow_id, user_id)
        )
        return cursor.rowcount > 0

def delete_workflow(workflow_id: int, user_id: int) -> bool:
    with get_db_connection("aria_workflows.db") as conn:
        cursor = execute_query(
            conn,
            "DELETE FROM workflows WHERE id = ? AND user_id = ?",
            (workflow_id, user_id)
        )
        return cursor.rowcount > 0

init_db()
