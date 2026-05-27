import os
import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Check if DATABASE_URL is set for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)

if IS_POSTGRES:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        logger.error("psycopg2 is required for PostgreSQL support. Install with: pip install psycopg2-binary")
        raise

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@contextmanager
def get_db_connection(db_name="aria.db"):
    """
    Context manager for database connections.
    Yields a connection object that works with standard cursor methods.
    """
    if IS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        # Resolve SQLite path. Vercel filesystem is read-only except /tmp
        if os.getenv("VERCEL") == "1":
            db_path = os.path.join("/tmp", db_name)
        else:
            db_path = os.path.join(os.path.dirname(__file__), "..", db_name)
            
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = dict_factory
        # Safe concurrent reads
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

def execute_query(conn, query: str, params: tuple = ()):
    """
    Executes a query, automatically translating '?' placeholders to '%s' for PostgreSQL.
    Returns the cursor.
    """
    if IS_POSTGRES:
        # Simple string replacement for placeholders.
        # This assumes '?' is not used inside string literals in the SQL queries.
        query = query.replace("?", "%s")
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor

def execute_script(conn, script: str):
    """
    Executes a multi-statement SQL script. 
    SQLite has executescript, psycopg2 can just run execute on multiple statements.
    """
    if IS_POSTGRES:
        cursor = conn.cursor()
        cursor.execute(script)
    else:
        conn.executescript(script)
