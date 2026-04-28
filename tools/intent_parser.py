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
        - unknown
        
        Examples:
        "What is the weather in Delhi?" -> weather
        "Search for AI news" -> search
        "Send email to john@gmail.com" -> email
        "How are you?" -> unknown
        
        Respond with just the single word, nothing else.
        """),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    intent = response.content.strip().lower()
    return intent