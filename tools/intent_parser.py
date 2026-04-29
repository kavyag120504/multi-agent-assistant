from tools.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

def parse_intent(user_message):
    llm = get_llm()

    messages = [
        SystemMessage(content="""
        You are an intent classifier. Given a user message,
        respond with ONLY one of these words:
        - weather
        - search
        - email
        - news
        - general

        Examples:
        "What is the weather in Delhi?" -> weather
        "Search for Python tutorials" -> search
        "Send email to john@gmail.com" -> email
        "What is the latest news about AI?" -> news
        "Tell me recent cricket news" -> news
        "What is 25 times 4?" -> general
        "How are you?" -> general
        "What is artificial intelligence?" -> general

        Respond with just the single word, nothing else.
        """),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    intent = response.content.strip().lower()
    return intent