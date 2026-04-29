from tools.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

def handle_general(user_message, memory=None):
    llm = get_llm()
    
    messages = [
        SystemMessage(content="""
        You are a helpful, friendly AI personal assistant.
        Answer questions clearly and concisely.
        You can handle general knowledge, math, advice, and casual conversation.
        If you remember previous messages, use that context.
        """)
    ]
    
    # Add memory history if available
    if memory:
        history = memory.get_history()
        messages.extend(history[-4:])  # last 4 messages for context
    
    messages.append(HumanMessage(content=user_message))
    
    response = llm.invoke(messages)
    return response.content.strip()