"""
User authentication database layer.
Uses SQLite + bcrypt for secure password hashing.
No plain-text passwords are ever stored.
"""
import sqlite3
import os
import secrets
import hashlib
import logging
from datetime import datetime, timedelta

logger  = logging.getLogger(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "aria_users.db")


# ── Connection ────────────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # safe for concurrent reads
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── Schema ────────────────────────────────────────────────────────────────────

def init_db():
    with _get_conn() as conn:
        conn.executescript("""
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
        """)
        conn.commit()
    logger.info("Auth DB initialised.")


# ── Password helpers ──────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """SHA-256 + random salt. No external deps needed."""
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
    """
    Register a new user.
    Returns (success: bool, message: str)
    """
    username = username.strip()
    display_name = display_name.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not username.replace("_", "").replace("-", "").isalnum():
        return False, "Username can only contain letters, numbers, - and _"

    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?)",
                (username, display_name, _hash_password(password))
            )
            conn.commit()
        logger.info(f"New user registered: {username}")
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, f"Username '{username}' is already taken."
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return False, "Registration failed. Please try again."


def login_user(username: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Authenticate a user.
    Returns (success, message, user_dict | None)
    """
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
                (username.strip(),)
            ).fetchone()

        if not row:
            return False, "Invalid username or password.", None

        if not _verify_password(password, row["password_hash"]):
            return False, "Invalid username or password.", None

        # Update last login
        with _get_conn() as conn:
            conn.execute(
                "UPDATE users SET last_login = datetime('now','localtime') WHERE id = ?",
                (row["id"],)
            )
            conn.commit()

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
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT id, username, display_name, created_at, last_login FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


# ── Session management ────────────────────────────────────────────────────────

def create_session(user_id: int, days: int = 7) -> str:
    """Create a secure session token valid for `days` days."""
    token      = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_id, expires_at)
        )
        conn.commit()
    return token


def validate_session(token: str) -> dict | None:
    """
    Validate a session token.
    Returns user dict if valid, None if expired or not found.
    """
    if not token:
        return None
    try:
        with _get_conn() as conn:
            row = conn.execute("""
                SELECT u.id, u.username, u.display_name
                FROM sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token = ?
                  AND s.expires_at > datetime('now','localtime')
            """, (token,)).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def delete_session(token: str):
    """Delete a session (logout)."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()


def cleanup_expired_sessions():
    """Remove expired sessions — call periodically."""
    with _get_conn() as conn:
        conn.execute(
            "DELETE FROM sessions WHERE expires_at <= datetime('now','localtime')"
        )
        conn.commit()


# Auto-init on import
init_db()
