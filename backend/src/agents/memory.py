"""
Memory Agent (Google ADK)

Retrieves chat history and analyzes weak topics from the user's profile.
"""

import logging
from typing import Dict, Any

from backend.src.services.memory_service import FirestoreChatMemory
from backend.src.services.firebase_service import get_firestore_client
from backend.src.config import settings

try:
    from google_adk.agent import Agent
except ImportError:
    class Agent:
        def __init__(self, name, description, instructions, llm=None):
            self.name = name
            self.description = description
            self.instructions = instructions
            self.llm = llm

logger = logging.getLogger("math_assistant.agents.memory")

class MemoryAgent(Agent):
    """Retrieves user memory and weak topics."""
    
    def __init__(self):
        super().__init__(
            name="MemoryAgent",
            description="Retrieves past conversation context and user weak topics.",
            instructions="Fetch user memory context."
        )

    def retrieve(self, uid: str, session_id: str) -> Dict[str, Any]:
        """Fetch history and weak topics."""
        # 1. Get Chat History
        memory_svc = FirestoreChatMemory(uid=uid, session_id=session_id)
        history = memory_svc.get_history(limit=5)
        
        formatted_history = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted_history.append(f"{role.capitalize()}: {content}")
            
        history_text = "\n".join(formatted_history) if formatted_history else "No previous conversation."

        # 2. Get Weak Topics
        weak_topics = []
        db = get_firestore_client()
        if db:
            try:
                doc = db.collection("users").document(uid).collection("profile").document("topics").get()
                if doc.exists:
                    weak_topics = doc.to_dict().get("weak_topics", [])
            except Exception as e:
                logger.error(f"Failed to fetch weak topics: {e}")
                
        return {
            "history": history_text,
            "weak_topics": weak_topics
        }
