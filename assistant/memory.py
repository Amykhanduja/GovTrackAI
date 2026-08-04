class ConversationMemory:
    def __init__(self, limit=10):
        self.limit = limit
        self.messages = []
        
    def add_user(self, text: str):
        self.messages.append({'role': 'user', 'content': text})
        if len(self.messages) > self.limit: self.messages.pop(0)
        
    def add_assistant(self, text: str):
        self.messages.append({'role': 'assistant', 'content': text})
        if len(self.messages) > self.limit: self.messages.pop(0)
        
    def get_history(self) -> str:
        return "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in self.messages])
