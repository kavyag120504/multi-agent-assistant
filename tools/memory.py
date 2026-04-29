from langchain_core.messages import HumanMessage, AIMessage

class ConversationMemory:
    def __init__(self):
        self.history = []
    
    def add_user_message(self, message):
        self.history.append(HumanMessage(content=message))
    
    def add_ai_message(self, message):
        self.history.append(AIMessage(content=message))
    
    def get_history(self):
        return self.history
    
    def get_history_as_text(self):
        text = ""
        for msg in self.history[-6:]:  # last 6 messages only
            if isinstance(msg, HumanMessage):
                text += f"User: {msg.content}\n"
            else:
                text += f"Assistant: {msg.content}\n"
        return text
    
    def clear(self):
        self.history = []