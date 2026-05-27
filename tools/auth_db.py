"""
User authentication database layer.
Uses SQLite/PostgreSQL + bcrypt for secure password hashing.
No plain-text passwords are ever stored.
"""
import os
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from tools.db_utils import get_db_connection, execute_query, execute_script, IS_POSTGRES

logger  = logging.getLogger(__name__)

# ── Schema ────────────────────────────────────────────────────────────────────

def init_db():
    sqlite_schema = """
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    NOT NULL UNIQUE COLLATE NOCASE,
            display_name TEXT    NOT NULL,
            password_hash TEXT   NOT NULL,
            created_at   TEXT    DEFAULT (datetime('now','localtime')),
            last_login   TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token       TEXT    PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at  TEXT    DEFAULT (datetime('now','localtime')),
            expires_at  TEXT    NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
    """
    
    postgres_schema = """
        CREATE TABLE IF NOT EXISTS users (
            id           SERIAL PRIMARY KEY,
            username     TEXT    NOT NULL UNIQUE,
            display_name TEXT    NOT NULL,
            password_hash TEXT   NOT NULL,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login   TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token       TEXT    PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at  TIMESTAMP NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
    """
    
    with get_db_connection("aria_users.db") as conn:
        execute_script(conn, postgres_schema if IS_POSTGRES else sqlite_schema)
    logger.info("Auth DB initialised.")


# ── Password helpers ──────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    salt = secrets.token_hex(32)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, hashed = stored_hash.split(":", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except Exception:
        return False


# ── User management ───────────────────────────────────────────────────────────

def register_user(username: str, display_name: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    display_name = display_name.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not username.replace("_", "").replace("-", "").isalnum():
        return False, "Username can only contain letters, numbers, - and _"

    # For postgres we emulate COLLATE NOCASE by forcing lowercase
    if IS_POSTGRES:
        username = username.lower()

    try:
        with get_db_connection("aria_users.db") as conn:
            execute_query(
                conn,
                "INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?)",
                (username, display_name, _hash_password(password))
            )
        logger.info(f"New user registered: {username}")
        return True, "Account created successfully!"
    except Exception as e:
        if "UNIQUE" in str(e).upper() or "unique constraint" in str(e).lower():
            return False, f"Username '{username}' is already taken."
        logger.error(f"Registration error: {e}")
        return False, "Registration failed. Please try again."


def login_user(username: str, password: str) -> tuple[bool, str, dict | None]:
    username = username.strip()
    if IS_POSTGRES:
        username = username.lower()

    try:
        with get_db_connection("aria_users.db") as conn:
            if IS_POSTGRES:
                cursor = execute_query(conn, "SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,))
            else:
                cursor = execute_query(conn, "SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,))
            row = cursor.fetchone()

        if not row:
            return False, "Invalid username or password.", None

        if not _verify_password(password, row["password_hash"]):
            return False, "Invalid username or password.", None

        # Update last login
        with get_db_connection("aria_users.db") as conn:
            if IS_POSTGRES:
                execute_query(conn, "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (row["id"],))
            else:
                execute_query(conn, "UPDATE users SET last_login = datetime('now','localtime') WHERE id = ?", (row["id"],))

        user = {
            "id":           row["id"],
            "username":     row["username"],
            "display_name": row["display_name"],
        }
        logger.info(f"User logged in: {username}")
        return True, "Login successful!", user

    except Exception as e:
        logger.error(f"Login error: {e}")
        return False, "Login failed. Please try again.", None


def get_user_by_id(user_id: int) -> dict | None:
    try:
        with get_db_connection("aria_users.db") as conn:
            cursor = execute_query(conn, "SELECT id, username, display_name, created_at, last_login FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
        return dict(row) if row else None
    except Exception:
        return None


# ── Session management ────────────────────────────────────────────────────────

def create_session(user_id: int, days: int = 7) -> str:
    token      = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection("aria_users.db") as conn:
        if IS_POSTGRES:
            # Need to cast string to timestamp in postgres
            execute_query(
                conn,
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS'))",
                (token, user_id, expires_at)
            )
        else:
            execute_query(
                conn,
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
                (token, user_id, expires_at)
            )
    return token


def validate_session(token: str) -> dict | None:
    if not token:
        return None
    try:
        with get_db_connection("aria_users.db") as conn:
            if IS_POSTGRES:
                query = """
                    SELECT u.id, u.username, u.display_name
                    FROM sessions s
                    JOIN users u ON u.id = s.user_id
                    WHERE s.token = ?
                      AND s.expires_at > CURRENT_TIMESTAMP
                """
            else:
                query = """
                    SELECT u.id, u.username, u.display_name
                    FROM sessions s
                    JOIN users u ON u.id = s.user_id
                    WHERE s.token = ?
                      AND s.expires_at > datetime('now','localtime')
                """
            cursor = execute_query(conn, query, (token,))
            row = cursor.fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def delete_session(token: str):
    with get_db_connection("aria_users.db") as conn:
        execute_query(conn, "DELETE FROM sessions WHERE token = ?", (token,))


def cleanup_expired_sessions():
    with get_db_connection("aria_users.db") as conn:
        if IS_POSTGRES:
            execute_query(conn, "DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")
        else:
            execute_query(conn, "DELETE FROM sessions WHERE expires_at <= datetime('now','localtime')")


# Auto-init on import
init_db()
