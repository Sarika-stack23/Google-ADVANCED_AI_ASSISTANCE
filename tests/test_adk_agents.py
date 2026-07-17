"""Tests for ADK Agents — Phase 4 Verification."""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.src.agents.planner import PlannerAgent
from backend.src.agents.verifier import VerifierAgent
from backend.src.agents.memory import MemoryAgent

class TestADKAgents(unittest.TestCase):
    """Verify individual ADK agents."""

    @patch("backend.src.agents.planner._get_llm")
    def test_planner_classification(self, mock_get_llm):
        """Test Planner classifying a question."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"type": "ncert_exercise", "class": 10}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        planner = PlannerAgent()
        # Ensure we inject the mock LLM after init
        planner.llm = mock_llm
        
        result = planner.plan("solve x^2+5x+6=0")
        
        self.assertEqual(result["type"], "ncert_exercise")
        self.assertEqual(result["class"], 10)

    @patch("backend.src.agents.verifier._get_llm")
    def test_verifier_catches_error(self, mock_get_llm):
        """Test Verifier agent catching a deliberate error."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"is_correct": false, "feedback": "4+4 equals 8, not 9."}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        verifier = VerifierAgent()
        verifier.llm = mock_llm
        
        result = verifier.verify("what is 4+4", "The answer is 4+4=9.")
        
        self.assertFalse(result["is_correct"])
        self.assertIn("4+4 equals 8", result["feedback"])

    @patch("backend.src.agents.memory.get_firestore_client")
    @patch("backend.src.agents.memory.FirestoreChatMemory")
    def test_memory_retrieves_weak_topics(self, mock_memory_cls, mock_get_db):
        """Test Memory agent fetching weak topics."""
        # Mock history
        mock_memory_instance = MagicMock()
        mock_memory_instance.get_history.return_value = [
            {"role": "user", "content": "Help me with algebra"}
        ]
        mock_memory_cls.return_value = mock_memory_instance
        
        # Mock Firestore topics
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"weak_topics": ["algebra", "quadratic_equations"]}
        mock_db.collection().document().collection().document().get.return_value = mock_doc
        mock_get_db.return_value = mock_db

        memory = MemoryAgent()
        result = memory.retrieve("test-uid", "test-session")
        
        self.assertIn("algebra", result["weak_topics"])
        self.assertIn("quadratic_equations", result["weak_topics"])
        self.assertIn("User: Help me with algebra", result["history"])

if __name__ == "__main__":
    unittest.main()
