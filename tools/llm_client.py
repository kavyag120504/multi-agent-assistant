from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

# ── Singleton LLM instance ───────────────────────────────────────────────────
# Created once at import time, reused across all agents for the session.
# This avoids re-initializing ChatGroq on every single agent call.
_llm_instance: ChatGroq | None = None

def get_llm() -> ChatGroq:
    global _llm_instance
    if _llm_instance is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY is missing from your .env file. "
                "Please add it and restart the app."
            )
        _llm_instance = ChatGroq(
            api_key=api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )
    return _llm_instance
