"""
Reminder agent — per-user isolation via SQLite.
Migrated from flat JSON file to DB so each user has their own reminders.
"""
import sqlite3
import uuid
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger  = logging.getLogger(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "aria_todos.db")


# ── DB helpers ────────────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _init_reminders_table():
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS reminders (
                id         TEXT    PRIMARY KEY,
                user_id    INTEGER NOT NULL DEFAULT 0,
                title      TEXT    NOT NULL,
                due        TEXT    DEFAULT 'no due time',
                note       TEXT    DEFAULT '',
                status     TEXT    DEFAULT 'pending',
                created_at TEXT    DEFAULT (datetime('now','localtime')),
                completed_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_reminders_user
                ON reminders(user_id, status);
        """)
        conn.commit()


_init_reminders_table()


def _load(user_id: int = 0) -> list:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM reminders WHERE user_id=? ORDER BY created_at ASC",
            (user_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def _save_reminder(r: dict, user_id: int = 0):
    with _get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO reminders
            (id, user_id, title, due, note, status, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"], user_id, r["title"], r.get("due", "no due time"),
            r.get("note", ""), r.get("status", "pending"),
            r.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M")),
            r.get("completed_at")
        ))
        conn.commit()


def _update_status(rid: str, status: str, user_id: int = 0):
    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M") if status == "done" else None
    with _get_conn() as conn:
        conn.execute(
            "UPDATE reminders SET status=?, completed_at=? WHERE id=? AND user_id=?",
            (status, completed_at, rid, user_id)
        )
        conn.commit()


def _delete_reminder_db(rid: str, user_id: int = 0):
    with _get_conn() as conn:
        conn.execute(
            "DELETE FROM reminders WHERE id=? AND user_id=?",
            (rid, user_id)
        )
        conn.commit()


def _clear_all_db(user_id: int = 0) -> int:
    with _get_conn() as conn:
        conn.execute("DELETE FROM reminders WHERE user_id=?", (user_id,))
        conn.commit()
        return conn.total_changes


# ── Main entry point ──────────────────────────────────────────────────────────

def handle_reminder(user_message: str, context: str = "",
                    user_id: int = 0) -> str:
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    try:
        llm          = get_llm()
        context_hint = f"\nConversation so far:\n{context}\n" if context else ""

        action_messages = [
            SystemMessage(content=f"""
            Classify the reminder/task request into one of:
            - add       (user wants to set/create/add a reminder)
            - list      (user wants to see/show/view all reminders)
            - done      (user wants to mark a reminder as complete/done)
            - delete    (user wants to delete/remove a specific reminder)
            - clear     (user wants to clear/delete ALL reminders)
            - overdue   (user wants to see overdue or missed reminders)

            Examples:
            "Remind me to call John at 5pm"          -> add
            "Set a reminder to submit report by 3pm" -> add
            "Show my reminders"                      -> list
            "Mark call John as done"                 -> done
            "Delete the grocery reminder"            -> delete
            "Clear all reminders"                    -> clear
            "What reminders did I miss?"             -> overdue
            {context_hint}
            Respond with just the single word.
            """),
            HumanMessage(content=user_message)
        ]
        action = llm.invoke(action_messages).content.strip().lower()
        if action not in ("add", "list", "done", "delete", "clear", "overdue"):
            action = "list"

        if action == "add":
            return _add_reminder(user_message, llm, user_id)
        elif action == "list":
            return _list_reminders(user_id)
        elif action == "done":
            return _mark_done(user_message, llm, user_id)
        elif action == "delete":
            return _delete_reminder(user_message, llm, user_id)
        elif action == "clear":
            return _clear_all(user_id)
        elif action == "overdue":
            return _list_overdue(user_id)

    except Exception as e:
        logger.error(f"Reminder agent error: {e}", exc_info=True)
        return f"⚠️ Reminder agent error: {str(e)}"


# ── ADD ───────────────────────────────────────────────────────────────────────

def _add_reminder(user_message: str, llm, user_id: int) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    extract_messages = [
        SystemMessage(content=f"""
        Extract reminder details from the user message.
        Current date and time: {now}

        Respond in this exact format, nothing else:
        TITLE: short task title
        DUE: YYYY-MM-DD HH:MM (or leave blank if no specific time)
        NOTE: any extra detail (or leave blank)
        """),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(extract_messages).content.strip()
    details  = {}
    for line in response.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            details[key.strip().upper()] = value.strip()

    title = details.get("TITLE", "").strip()
    due   = details.get("DUE", "").strip()
    note  = details.get("NOTE", "").strip()

    if not title:
        return "❓ I couldn't understand the reminder. Try: *\"Remind me to call John at 5pm\"*"

    due_str    = ""
    due_status = "no due time"
    if due:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                due_dt     = datetime.strptime(due, fmt)
                due_str    = due_dt.strftime("%b %d, %Y at %I:%M %p")
                due_status = due
                break
            except ValueError:
                continue

    reminder = {
        "id":         str(uuid.uuid4())[:8],
        "title":      title,
        "due":        due_status,
        "note":       note,
        "status":     "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _save_reminder(reminder, user_id)

    return (
        f"✅ **Reminder set!**\n"
        f"📌 **{title}**\n"
        f"🕐 Due: {due_str or 'No specific time'}\n"
        f"🆔 ID: `{reminder['id']}`"
        + (f"\n📝 Note: {note}" if note else "")
    )


# ── LIST ──────────────────────────────────────────────────────────────────────

def _list_reminders(user_id: int) -> str:
    reminders = _load(user_id)
    pending   = [r for r in reminders if r.get("status") == "pending"]

    if not reminders:
        return "📋 You have no reminders. Try: *\"Remind me to call John at 5pm\"*"

    if not pending:
        done_count = len([r for r in reminders if r.get("status") == "done"])
        return f"✅ All caught up! You have **{done_count}** completed reminder(s)."

    now    = datetime.now()
    output = f"📋 **Your Pending Reminders ({len(pending)}):**\n\n"

    for r in pending:
        title       = r.get("title", "Untitled")
        due         = r.get("due", "")
        rid         = r.get("id", "")
        note        = r.get("note", "")
        overdue_tag = ""

        if due and due != "no due time":
            try:
                if datetime.strptime(due, "%Y-%m-%d %H:%M") < now:
                    overdue_tag = " 🔴 **OVERDUE**"
            except ValueError:
                pass

        output += f"📌 **{title}**{overdue_tag}\n"
        output += f"   🕐 Due: {due if due and due != 'no due time' else 'No specific time'}\n"
        output += f"   🆔 ID: `{rid}`"
        if note:
            output += f"\n   📝 {note}"
        output += "\n\n"

    return output


# ── MARK DONE ─────────────────────────────────────────────────────────────────

def _mark_done(user_message: str, llm, user_id: int) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    reminders = _load(user_id)
    pending   = [r for r in reminders if r.get("status") == "pending"]

    if not pending:
        return "📋 You have no pending reminders to mark as done."

    task_list = "\n".join(
        f"{i}: [{r['id']}] {r['title']} (due: {r.get('due', 'no due time')})"
        for i, r in enumerate(pending)
    )

    match_messages = [
        SystemMessage(content=f"""
        The user wants to mark a reminder as done.
        Pending reminders:
        {task_list}
        Respond with ONLY the index number (0-based). If no match: -1
        """),
        HumanMessage(content=user_message)
    ]
    try:
        index = int(llm.invoke(match_messages).content.strip())
    except ValueError:
        index = -1

    if index == -1 or index >= len(pending):
        return "❌ Couldn't match that reminder. Try using the task name more clearly."

    _update_status(pending[index]["id"], "done", user_id)
    return f"✅ Marked as done: **{pending[index]['title']}**"


# ── DELETE ────────────────────────────────────────────────────────────────────

def _delete_reminder(user_message: str, llm, user_id: int) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    reminders = _load(user_id)

    if not reminders:
        return "📋 You have no reminders to delete."

    task_list = "\n".join(
        f"{i}: [{r['id']}] {r['title']} ({r.get('status', 'pending')})"
        for i, r in enumerate(reminders)
    )

    match_messages = [
        SystemMessage(content=f"""
        The user wants to delete a reminder.
        All reminders:
        {task_list}
        Respond with ONLY the index number (0-based). If no match: -1
        """),
        HumanMessage(content=user_message)
    ]
    try:
        index = int(llm.invoke(match_messages).content.strip())
    except ValueError:
        index = -1

    if index == -1 or index >= len(reminders):
        return "❌ Couldn't find that reminder. Try using the task name more clearly."

    removed = reminders[index]
    _delete_reminder_db(removed["id"], user_id)
    return f"🗑️ Deleted reminder: **{removed['title']}**"


# ── CLEAR ALL ─────────────────────────────────────────────────────────────────

def _clear_all(user_id: int) -> str:
    count = _clear_all_db(user_id)
    return (f"🗑️ Cleared all **{count}** reminder(s)."
            if count else "📋 No reminders to clear.")


# ── OVERDUE ───────────────────────────────────────────────────────────────────

def _list_overdue(user_id: int) -> str:
    reminders = _load(user_id)
    now       = datetime.now()
    overdue   = []

    for r in reminders:
        if r.get("status") != "pending":
            continue
        due = r.get("due", "")
        if due and due != "no due time":
            try:
                if datetime.strptime(due, "%Y-%m-%d %H:%M") < now:
                    overdue.append(r)
            except ValueError:
                pass

    if not overdue:
        return "✅ No overdue reminders. You're all caught up!"

    output = f"🔴 **Overdue Reminders ({len(overdue)}):**\n\n"
    for r in overdue:
        title = r.get("title", "Untitled")
        due   = r.get("due", "")
        rid   = r.get("id", "")
        try:
            due_dt    = datetime.strptime(due, "%Y-%m-%d %H:%M")
            time_ago  = now - due_dt
            hours_ago = int(time_ago.total_seconds() // 3600)
            mins_ago  = int((time_ago.total_seconds() % 3600) // 60)
            ago_str   = f"{hours_ago}h {mins_ago}m ago" if hours_ago else f"{mins_ago}m ago"
        except Exception:
            ago_str = "unknown time ago"

        output += f"📌 **{title}**\n"
        output += f"   🕐 Was due: {due}  ({ago_str})\n"
        output += f"   🆔 ID: `{rid}`\n\n"

    return output
