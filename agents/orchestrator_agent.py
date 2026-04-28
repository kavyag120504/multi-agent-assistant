from tools.intent_parser import parse_intent
from agents.weather_agent import get_weather
from agents.search_agent import search_web
from agents.email_agent import send_email

def run_assistant(user_message):
    print(f"User said: {user_message}")
    
    # Step 1: Detect intent
    intent = parse_intent(user_message)
    print(f"Detected intent: {intent}")
    
    # Step 2: Route to correct agent
    if intent == "weather":
        response = get_weather(user_message)
    
    elif intent == "search":
        response = search_web(user_message)
    
    elif intent == "email":
        response = send_email(user_message)
    
    else:
        # Handle general conversation directly with LLM
        from tools.llm_client import get_llm
        from langchain_core.messages import HumanMessage, SystemMessage
        
        llm = get_llm()
        messages = [
            SystemMessage(content="""
            You are a helpful AI personal assistant. 
            Answer the user's question in a friendly and concise way.
            """),
            HumanMessage(content=user_message)
        ]
        response = llm.invoke(messages).content.strip()
    
    return response