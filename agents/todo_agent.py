import json
import re
from tools.llm_client import get_llm
from tools.todo_db import add_task, get_tasks, complete_task, delete_task
from langchain_core.messages import HumanMessage

EXTRACT_PROMPT = """Extract the todo action from this message. Return ONLY valid JSON.

Actions: add_task | view_tasks | complete_task | delete_task

For add_task return:
{{"action": "add_task", "task": "...", "due_date": "YYYY-MM-DD or null", "priority": "high|normal|low"}}

For view_tasks return:
{{"action": "view_tasks", "filter": "pending|done|all"}}

For complete_task / delete_task return:
{{"action": "complete_task", "task_id": <number>}}
or
{{"action": "delete_task", "task_id": <number>}}

Message: {message}
"""


def _parse_action(message: str) -> dict:
    llm  = get_llm()
    resp = llm.invoke([HumanMessage(content=EXTRACT_PROMPT.format(message=message))])
    raw  = resp.content.strip()
    raw  = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(raw)


def handle_todo(message: str, user_id: int = 0) -> str:
    try:
        action = _parse_action(message)
    except Exception:
        return (
            "❓ I couldn't understand that task request.\n"
            "Try:\n"
            "- *\"Add task buy milk\"*\n"
            "- *\"Show my pending tasks\"*\n"
            "- *\"Complete task 3\"*\n"
            "- *\"Delete task 5\"*"
        )

    a = action.get("action")

    # ── ADD ──────────────────────────────────────────────────────────────────
    if a == "add_task":
        task     = action.get("task", "Unnamed task")
        due_date = action.get("due_date")
        priority = action.get("priority", "normal")

        if priority not in ("high", "normal", "low"):
            priority = "normal"

        task_id       = add_task(task=task, user_id=user_id,
                                 due_date=due_date, priority=priority)
        due_str       = f" · due **{due_date}**" if due_date else ""
        priority_icon = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(priority, "🟡")

        return (
            f"✅ **Task added!**\n"
            f"📌 [{task_id}] {task}{due_str}\n"
            f"{priority_icon} Priority: {priority}"
        )

    # ── VIEW ─────────────────────────────────────────────────────────────────
    elif a == "view_tasks":
        filter_by = action.get("filter", "pending")
        tasks     = get_tasks(filter=filter_by, user_id=user_id)

        if not tasks:
            label = {"pending": "pending", "done": "completed", "all": ""}.get(filter_by, "")
            return f"📋 No {label} tasks found. Try: *\"Add task buy milk\"*"

        label  = {"pending": "Pending Tasks", "done": "Completed Tasks",
                  "all": "All Tasks"}.get(filter_by, "Tasks")
        output = f"📋 **{label} ({len(tasks)}):**\n\n"

        for t in tasks:
            status_icon = "✅" if t["done"] else {
                "high": "🔴", "normal": "🟡", "low": "🟢"
            }.get(t["priority"], "🟡")
            due_str  = f" · due {t['due_date']}" if t["due_date"] else ""
            output  += f"{status_icon} **[#{t['id']}]** {t['task']}{due_str}\n"

        return output

    # ── COMPLETE ─────────────────────────────────────────────────────────────
    elif a == "complete_task":
        tid = action.get("task_id")
        if tid is None:
            return "❓ Please specify the task ID. Try: *\"Complete task 3\"*"
        ok = complete_task(int(tid), user_id=user_id)
        return (f"✅ Task **#{tid}** marked as done!"
                if ok else f"❌ No task found with ID **#{tid}**.")

    # ── DELETE ────────────────────────────────────────────────────────────────
    elif a == "delete_task":
        tid = action.get("task_id")
        if tid is None:
            return "❓ Please specify the task ID. Try: *\"Delete task 5\"*"
        ok = delete_task(int(tid), user_id=user_id)
        return (f"🗑️ Task **#{tid}** deleted."
                if ok else f"❌ No task found with ID **#{tid}**.")

    return (
        "❓ I'm not sure what task action you meant.\n"
        "Try: *\"Add task\"*, *\"Show tasks\"*, "
        "*\"Complete task 3\"*, or *\"Delete task 5\"*"
    )
