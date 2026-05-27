import logging
import time
from tools.intent_parser import parse_intents
from tools.memory import ConversationMemory
from tools.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

from agents.weather_agent import get_weather
from agents.search_agent import search_web
from agents.email_agent import handle_email
from agents.news_agent import get_news
from agents.general_agent import handle_general
from agents.calendar_agent import handle_calendar
from agents.reminder_agent import handle_reminder
from agents.todo_agent import handle_todo
from agents.code_agent import handle_code

logger = logging.getLogger(__name__)

# Per-user memory cache: {user_id: ConversationMemory}
_memory_cache: dict[int | None, ConversationMemory] = {}

def get_memory(user_id: int = None) -> ConversationMemory:
    """Return (or create) a ConversationMemory instance for this user."""
    if user_id not in _memory_cache:
        _memory_cache[user_id] = ConversationMemory(user_id=user_id)
    return _memory_cache[user_id]

def _run_single_agent(intent: str, user_message: str, context: str, user_id: int, memory: ConversationMemory):
    """Executes a single agent and returns its output."""
    try:
        if intent == "weather":
            return get_weather(user_message, context)
        elif intent == "search":
            return search_web(user_message, context)
        elif intent == "email":
            return handle_email(user_message, context)
        elif intent == "news":
            return get_news(user_message, context)
        elif intent == "calendar":
            return handle_calendar(user_message, context)
        elif intent == "reminder":
            return handle_reminder(user_message, context, user_id=user_id or 0)
        elif intent == "todo":
            return handle_todo(user_message, user_id=user_id or 0)
        elif intent == "code":
            return handle_code(user_message, context)
        else:
            return handle_general(user_message, memory)
    except Exception as e:
        logger.error(f"[user={user_id}] Agent '{intent}' unhandled exception: {e}", exc_info=True)
        return f"Error executing {intent} agent: {str(e)}"

def run_assistant(user_message: str, user_id: int = None):
    """
    Process a user message using Multi-Agent Orchestration.
    Returns (response, intent, confidence, agent_runs).
    """
    if not user_message or not user_message.strip():
        return "❓ Please type a message so I can help you.", "general", 100, []

    user_message = user_message.strip()
    memory = get_memory(user_id)
    memory.add_user_message(user_message)
    context = memory.get_context_text(n=6)

    # 1. Intent Parsing (Multi-Agent)
    intents = parse_intents(user_message)
    logger.info(f"[user={user_id}] Intents: {intents} | Message: '{user_message[:60]}'")
    
    agent_runs = []
    agent_outputs = {}
    
    # 2. Execute Agents
    for intent in intents:
        start_time = time.time()
        
        # We don't want the general agent running parallel to specific ones unless requested, 
        # but if it is, we collect its reasoning too.
        output = _run_single_agent(intent, user_message, context, user_id, memory)
        
        execution_time = round((time.time() - start_time) * 1000) # ms
        
        agent_runs.append({
            "agent": intent,
            "status": "completed" if not str(output).startswith("Error") else "failed",
            "execution_time_ms": execution_time,
            "summary": output[:100] + "..." if len(str(output)) > 100 else output
        })
        agent_outputs[intent] = output

    # 3. Synthesize if Multiple Agents, otherwise return single result
    confidence = 100
    primary_intent = intents[0] if intents else "general"
    
    if len(intents) == 1 and primary_intent != "general":
        # Direct result
        final_response = agent_outputs[primary_intent]
        confidence = 90
    else:
        # Multi-agent synthesis or single general agent
        llm = get_llm()
        
        synthesis_prompt = f"""
        You are KAVI, an advanced AI assistant. You have orchestrated multiple specialized agents to answer the user's query.
        Synthesize their outputs into a single, cohesive, and helpful response.
        
        User Query: {user_message}
        
        Agent Outputs:
        """
        for k, v in agent_outputs.items():
            synthesis_prompt += f"\n--- {k.upper()} AGENT ---\n{v}\n"
            
        synthesis_prompt += "\nSynthesize a final response. Do not explain the orchestration process to the user, just answer their query directly based on the provided data."
        
        try:
            response_msg = llm.invoke([
                SystemMessage(content="You are KAVI, a helpful multi-agent AI assistant."),
                HumanMessage(content=synthesis_prompt)
            ])
            final_response = response_msg.content.strip()
            confidence = 80 if len(intents) > 1 else 70
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            final_response = "⚠️ I gathered some information but encountered an error synthesizing the final response."
            confidence = 30
            
    memory.add_ai_message(final_response, intent="multi-agent" if len(intents) > 1 else primary_intent)
    
    return final_response, "multi-agent" if len(intents) > 1 else primary_intent, confidence, agent_runs

def clear_memory(user_id: int = None):
    memory = get_memory(user_id)
    memory.clear()
    _memory_cache.pop(user_id, None)
    logger.info(f"Memory cleared for user={user_id}")
