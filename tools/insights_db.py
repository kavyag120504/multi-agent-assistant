import logging
from tools.db_utils import get_db_connection, execute_query, execute_script, IS_POSTGRES

logger = logging.getLogger(__name__)

def init_db():
    sqlite_schema = """
        CREATE TABLE IF NOT EXISTS insights (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            title            TEXT NOT NULL,
            description      TEXT NOT NULL,
            type             TEXT,
            priority         TEXT,
            suggested_action TEXT,
            source_agents    TEXT,
            dismissed        INTEGER DEFAULT 0,
            created_at       TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_insights_user ON insights(user_id, dismissed);
    """
    
    postgres_schema = """
        CREATE TABLE IF NOT EXISTS insights (
            id               SERIAL PRIMARY KEY,
            user_id          INTEGER NOT NULL,
            title            TEXT NOT NULL,
            description      TEXT NOT NULL,
            type             TEXT,
            priority         TEXT,
            suggested_action TEXT,
            source_agents    TEXT,
            dismissed        INTEGER DEFAULT 0,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_insights_user ON insights(user_id, dismissed);
    """

    with get_db_connection("aria_insights.db") as conn:
        execute_script(conn, postgres_schema if IS_POSTGRES else sqlite_schema)

def add_insight(user_id: int, title: str, description: str, type: str, priority: str, suggested_action: str, source_agents: str) -> int:
    with get_db_connection("aria_insights.db") as conn:
        cursor = execute_query(
            conn,
            """INSERT INTO insights 
               (user_id, title, description, type, priority, suggested_action, source_agents) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""" + (" RETURNING id" if IS_POSTGRES else ""),
            (user_id, title, description, type, priority, suggested_action, source_agents)
        )
        return cursor.fetchone()["id"] if IS_POSTGRES else cursor.lastrowid

def get_insights(user_id: int, include_dismissed: bool = False) -> list:
    with get_db_connection("aria_insights.db") as conn:
        query = "SELECT * FROM insights WHERE user_id = ?"
        params = [user_id]
        if not include_dismissed:
            query += " AND dismissed = 0"
        query += " ORDER BY priority DESC, created_at DESC"
        
        cursor = execute_query(conn, query, tuple(params))
        return [dict(r) for r in cursor.fetchall()]

def dismiss_insight(insight_id: int, user_id: int) -> bool:
    with get_db_connection("aria_insights.db") as conn:
        cursor = execute_query(
            conn,
            "UPDATE insights SET dismissed = 1 WHERE id = ? AND user_id = ?",
            (insight_id, user_id)
        )
        return cursor.rowcount > 0

init_db()
