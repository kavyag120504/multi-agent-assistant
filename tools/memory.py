from langchain_core.messages import HumanMessage, AIMessage
from tools.user_memory_db import (
    save_message,
    load_history,
    get_context_text as db_context_text,
    clear_history,
)


class ConversationMemory:
    """
    In-memory conversation store that optionally syncs to SQLite.

    When user_id is set (logged-in user), every message is persisted
    to the DB and history is loaded from DB on init — survives refreshes.

    When user_id is None (anonymous), behaves exactly as before.
    """

    def __init__(self, user_id: int = None):
        self.user_id  = user_id
        self.history: list = []

        # Load existing history from DB if user is logged in
        if user_id is not None:
            self._load_from_db()

    def _load_from_db(self):
        """Populate in-memory history from DB on startup."""
        rows = load_history(self.user_id, limit=50)
        for row in rows:
            if row["role"] == "user":
                self.history.append(HumanMessage(content=row["content"]))
            else:
                self.history.append(AIMessage(content=row["content"]))

    def add_user_message(self, message: str):
        self.history.append(HumanMessage(content=message))
        if self.user_id is not None:
            save_message(self.user_id, "user", message)

    def add_ai_message(self, message: str, intent: str = None):
        self.history.append(AIMessage(content=message))
        if self.user_id is not None:
            save_message(self.user_id, "assistant", message, intent)

    def get_history(self) -> list:
        """Return full history as LangChain message objects."""
        return self.history

    def get_recent(self, n: int = 6) -> list:
        """Return last n messages as LangChain message objects."""
        return self.history[-n:]

    def get_context_text(self, n: int = 6) -> str:
        """
        Return last n messages as plain text for agent context injection.
        Uses DB directly when user is logged in (more efficient for large histories).
        """
        if self.user_id is not None:
            return db_context_text(self.user_id, n=n)

        text = ""
        for msg in self.history[-n:]:
            if isinstance(msg, HumanMessage):
                text += f"User: {msg.content}\n"
            else:
                text += f"Assistant: {msg.content}\n"
        return text.strip()

    # Backward compatibility alias
    def get_history_as_text(self) -> str:
        return self.get_context_text()

    def clear(self):
        self.history = []
        if self.user_id is not None:
            clear_history(self.user_id)
