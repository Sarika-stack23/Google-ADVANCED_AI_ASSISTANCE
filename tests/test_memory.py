"""Tests for MongoDBChatMemory — extracted from main.py L2658-L2670.

Validates chat memory add/retrieve operations and LangChain message
conversion. Uses in-memory fallback when MongoDB is not available.
"""

import unittest
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import MongoDBChatMemory

try:
    from langchain_core.messages import HumanMessage
except ImportError:
    from langchain.schema import HumanMessage


class TestMemory(unittest.TestCase):
    """Verify chat memory stores and retrieves messages correctly."""

    def test_add_retrieve(self):
        """Adding two messages should result in at least two in history."""
        mem = MongoDBChatMemory(session_id="test")
        mem.add_message("human", "What is a derivative?")
        mem.add_message("assistant", "Rate of change.")
        self.assertGreaterEqual(len(mem.get_history()), 2)

    def test_langchain_messages(self):
        """LangChain message conversion should produce HumanMessage objects."""
        mem = MongoDBChatMemory(session_id="test_lc")
        mem.add_message("human", "Test")
        mem.add_message("assistant", "Answer")
        msgs = mem.get_langchain_messages()
        self.assertTrue(any(isinstance(m, HumanMessage) for m in msgs))


if __name__ == "__main__":
    unittest.main()
