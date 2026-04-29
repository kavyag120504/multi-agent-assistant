from tools.intent_parser import parse_intent
from tools.memory import ConversationMemory
from agents.weather_agent import get_weather
from agents.search_agent import search_web
from agents.email_agent import send_email
from agents.news_agent import get_news
from agents.general_agent import handle_general

# One memory instance for the whole session
memory = ConversationMemory()

def run_assistant(user_message):
    # Save user message to memory
    memory.add_user_message(user_message)
    
    # Detect intent
    intent = parse_intent(user_message)
    print(f"Intent: {intent}")
    
    # Route to correct agent
    if intent == "weather":
        response = get_weather(user_message)
    elif intent == "search":
        response = search_web(user_message)
    elif intent == "email":
        response = send_email(user_message)
    elif intent == "news":
        response = get_news(user_message)
    else:
        response = handle_general(user_message, memory)
    
    # Save response to memory
    memory.add_ai_message(response)
    
    return response, intent

def clear_memory():
    memory.clear()