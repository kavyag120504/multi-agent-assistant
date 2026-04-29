import logging
from tools.intent_parser import parse_intent
from tools.memory import ConversationMemory
from agents.weather_agent import get_weather
from agents.search_agent import search_web
from agents.email_agent import handle_email
from agents.news_agent import get_news
from agents.general_agent import handle_general
from agents.calendar_agent import handle_calendar
from agents.reminder_agent import handle_reminder
from agents.todo_agent import handle_todo
from agents.code_agent import handle_code

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("aria.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Per-user memory cache: {user_id: ConversationMemory}
# Anonymous users get user_id=None and share a single instance
_memory_cache: dict[int | None, ConversationMemory] = {}


def get_memory(user_id: int = None) -> ConversationMemory:
    """Return (or create) a ConversationMemory instance for this user."""
    if user_id not in _memory_cache:
        _memory_cache[user_id] = ConversationMemory(user_id=user_id)
    return _memory_cache[user_id]


def run_assistant(user_message: str, user_id: int = None):
    """
    Process a user message and return (response, intent).
    user_id: logged-in user's DB id, or None for anonymous.
    """
    if not user_message or not user_message.strip():
        return "❓ Please type a message so I can help you.", "general"

    user_message = user_message.strip()
    memory       = get_memory(user_id)
    memory.add_user_message(user_message)

    # ── Detect intent ────────────────────────────────────────────────────────
    try:
        intent = parse_intent(user_message)
        logger.info(
            f"[user={user_id}] Intent: '{intent}' | "
            f"Message: '{user_message[:60]}'"
        )
    except Exception as e:
        logger.error(f"Intent parsing failed: {e}")
        intent = "general"

    # ── Build context for agents ─────────────────────────────────────────────
    context = memory.get_context_text(n=6)

    # ── Route to correct agent ───────────────────────────────────────────────
    try:
        if intent == "weather":
            response = get_weather(user_message, context)
        elif intent == "search":
            response = search_web(user_message, context)
        elif intent == "email":
            response = handle_email(user_message, context)
        elif intent == "news":
            response = get_news(user_message, context)
        elif intent == "calendar":
            response = handle_calendar(user_message, context)
        elif intent == "reminder":
            response = handle_reminder(user_message, context, user_id=user_id or 0)
        elif intent == "todo":
            response = handle_todo(user_message, user_id=user_id or 0)
        elif intent == "code":
            response = handle_code(user_message, context)
        else:
            response = handle_general(user_message, memory)

    except Exception as e:
        logger.error(
            f"[user={user_id}] Agent '{intent}' unhandled exception: {e}",
            exc_info=True
        )
        response = (
            "⚠️ Something went wrong while processing your request. "
            "Please try again or rephrase your message."
        )

    memory.add_ai_message(response, intent=intent)
    return response, intent


def clear_memory(user_id: int = None):
    memory = get_memory(user_id)
    memory.clear()
    # Remove from cache so next call creates a fresh instance
    _memory_cache.pop(user_id, None)
    logger.info(f"Memory cleared for user={user_id}")
