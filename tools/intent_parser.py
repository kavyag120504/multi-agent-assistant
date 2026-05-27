import json
from tools.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

_VALID_INTENTS = {
    "weather", "search", "email", "news",
    "calendar", "reminder", "todo", "code", "general"
}

def parse_intents(user_message: str) -> list[str]:
    llm = get_llm()

    messages = [
        SystemMessage(content="""
        You are an advanced intent classifier for a multi-agent platform.
        Analyze the user's message and return a JSON list of required agent intents.
        Valid intents are: weather, search, email, news, calendar, reminder, todo, code, general.

        Examples:
        "What is the weather in Delhi?" -> ["weather"]
        "Should I travel to Mumbai this weekend?" -> ["weather", "calendar", "general"]
        "Summarize today's AI news and email it to my team." -> ["news", "general", "email"]
        "Am I free tomorrow and what's the weather there?" -> ["calendar", "weather"]
        "Calculate sqrt(144)" -> ["general"]
        "Add task buy groceries" -> ["todo"]

        Respond ONLY with a valid JSON array of strings, nothing else. No markdown formatting.
        """),
        HumanMessage(content=user_message)
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        # Clean up possible markdown code blocks if the LLM ignores instructions
        if content.startswith("```json"):
            content = content.replace("```json", "", 1)
        if content.endswith("```"):
            content = content[:-3]
            
        intents = json.loads(content.strip())
        if not isinstance(intents, list):
            intents = ["general"]
            
        # Filter valid intents
        valid_found = [i for i in intents if i in _VALID_INTENTS]
        return valid_found if valid_found else ["general"]
    except Exception as e:
        return ["general"]
