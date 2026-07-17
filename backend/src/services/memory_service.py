"""
Chat Memory Service — MongoDB-backed persistent chat history.

Extracted from main.py L525-L582. Provides per-session chat history
with MongoDB persistence and in-memory fallback when MongoDB is unavailable.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict

from backend.src.config import settings

try:
    from langchain_core.messages import HumanMessage, AIMessage
except ImportError:
    from langchain.schema import HumanMessage, AIMessage

logger = logging.getLogger("math_assistant.memory")


class MongoDBChatMemory:
    """Per-session chat memory with MongoDB persistence and in-memory fallback."""

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.collection = None
        self._memory: List[Dict] = []
        self._connect()

    def _connect(self):
        if not settings.mongodb_uri:
            return
        try:
            from pymongo import MongoClient
            client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            self.collection = client[settings.mongodb_db_name][settings.mongodb_collection]
            logger.info("MongoDB connected")
        except Exception as e:
            logger.warning(f"MongoDB unavailable ({e}), using in-memory history")

    def add_message(self, role: str, content: str):
        """Add a message to chat history."""
        msg = {
            "session_id": self.session_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc),
        }
        if self.collection is not None:
            try:
                self.collection.insert_one(msg)
                return
            except Exception:
                pass
        self._memory.append(msg)

    def get_history(self, limit: int = 20) -> List[Dict]:
        """Retrieve recent chat history for this session."""
        if self.collection is not None:
            try:
                msgs = list(
                    self.collection.find({"session_id": self.session_id})
                    .sort("timestamp", -1)
                    .limit(limit)
                )
                msgs.reverse()
                return msgs
            except Exception:
                pass
        return self._memory[-limit:]

    def get_langchain_messages(self, limit: int = 10):
        """Convert chat history to LangChain message objects."""
        history = self.get_history(limit)
        result = []
        for msg in history:
            if msg["role"] == "human":
                result.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                result.append(AIMessage(content=msg["content"]))
        return result

    def clear_history(self):
        """Clear all messages for this session."""
        if self.collection is not None:
            try:
                self.collection.delete_many({"session_id": self.session_id})
            except Exception:
                pass
        self._memory.clear()
