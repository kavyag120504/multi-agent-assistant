import logging
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

logger   = logging.getLogger(__name__)
_started = False  # guard — prevents duplicate schedulers on Streamlit reruns


def _build_reminder_message(tasks: list) -> str:
    """Format due/overdue tasks into a clean Telegram message."""
    today = str(date.today())
    lines = ["🤖 *ARIA Reminder*\n"]

    overdue = [t for t in tasks if t["due_date"] and t["due_date"] < today]
    due_today = [t for t in tasks if t["due_date"] == today]
    no_date = [t for t in tasks if not t["due_date"]]

    if overdue:
        lines.append("🔴 *Overdue:*")
        for t in overdue:
            lines.append(f"  • [#{t['id']}] {t['task']} _(was due {t['due_date']})_")

    if due_today:
        lines.append("\n🟡 *Due today:*")
        for t in due_today:
            lines.append(f"  • [#{t['id']}] {t['task']}")

    if no_date and not overdue and not due_today:
        lines.append("📋 *Pending tasks (no due date):*")
        for t in no_date[:5]:  # cap at 5 to avoid huge messages
            lines.append(f"  • [#{t['id']}] {t['task']}")

    lines.append(f"\n_Open ARIA to manage your tasks._")
    return "\n".join(lines)


def _check_and_notify():
    """Called by the scheduler — checks due tasks and sends Telegram message."""
    try:
        from tools.todo_db import get_tasks
        from tools.telegram_notifier import send_telegram

        today   = str(date.today())
        tasks   = get_tasks("pending", user_id=0)  # scheduler notifies the primary account
        # Only notify if there are tasks due today or overdue
        due     = [t for t in tasks if t["due_date"] and t["due_date"] <= today]

        if not due:
            logger.info("Scheduler: no due tasks today, skipping notification.")
            return

        message = _build_reminder_message(tasks)
        sent    = send_telegram(message)

        if sent:
            logger.info(f"Scheduler: Telegram reminder sent for {len(due)} task(s).")
        else:
            logger.warning("Scheduler: Telegram send failed — check your .env credentials.")

    except Exception as e:
        logger.error(f"Scheduler job error: {e}", exc_info=True)


def start_scheduler():
    """
    Start the APScheduler background scheduler.
    Safe to call multiple times — the _started guard prevents duplicates.

    Schedule: every day at 9:00 AM local time.
    To change the time, edit the hour/minute values below.
    """
    global _started
    if _started:
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            _check_and_notify,
            trigger="cron",
            hour=int(os.getenv("REMINDER_HOUR", "9")),    # default 9am
            minute=int(os.getenv("REMINDER_MINUTE", "0")), # default :00
            id="daily_reminder",
            replace_existing=True,
        )
        scheduler.start()
        _started = True
        logger.info(
            f"Reminder scheduler started — fires daily at "
            f"{os.getenv('REMINDER_HOUR', '9')}:{os.getenv('REMINDER_MINUTE', '00')} "
            f"(local time)."
        )

    except ImportError:
        logger.warning(
            "APScheduler not installed. Run: pip install apscheduler\n"
            "Telegram reminders will not fire until it is installed."
        )
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}", exc_info=True)
