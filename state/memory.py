# Memory and conversation state management utilities
from typing import Dict, List, Any

class ConversationMemory:
    """Simple in-memory conversation state management"""
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_message(self, thread_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to a conversation thread"""
        if thread_id not in self.conversations:
            self.conversations[thread_id] = []
        
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.conversations[thread_id].append(message)
    
    def get_conversation(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a conversation thread"""
        return self.conversations.get(thread_id, [])
    
    def clear_conversation(self, thread_id: str):
        """Clear a conversation thread"""
        if thread_id in self.conversations:
            del self.conversations[thread_id]

# Global memory instance
memory = ConversationMemory()
