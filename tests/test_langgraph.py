"""Tests for LangGraph Workflow — Phase 5 Verification."""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.src.graph.math_graph import math_graph

class TestLangGraph(unittest.TestCase):
    """Verify LangGraph transitions and states."""

    @patch("backend.src.graph.nodes.nodes._get_agent")
    @patch("backend.src.graph.nodes.nodes.FirestoreChatMemory")
    def test_successful_graph_run(
        self, mock_memory_cls, mock_get_agent
    ):
        """Test a clean run where verification passes immediately."""
        
        # Setup mock agents
        mock_planner = MagicMock()
        mock_planner.plan.return_value = {"type": "ncert_exercise", "class": 10}
        
        mock_solver = MagicMock()
        mock_solver.retrieve_context.return_value = "Rag context"
        mock_solver.solve.return_value = "Solution is 4."
        
        mock_memory_agent = MagicMock()
        mock_memory_agent.retrieve.return_value = {"history": "history", "weak_topics": ["algebra"]}
        
        mock_verifier = MagicMock()
        mock_verifier.verify.return_value = {"is_correct": True, "feedback": "Looks good."}
        
        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Solution: 4."
        
        def side_effect(agent_cls, name):
            if name == "planner": return mock_planner
            if name == "solver": return mock_solver
            if name == "memory": return mock_memory_agent
            if name == "verifier": return mock_verifier
            if name == "formatter": return mock_formatter
            
        mock_get_agent.side_effect = side_effect

        initial_state = {
            "user_query": "What is 2+2?",
            "uid": "test_uid",
            "session_id": "test_session",
            "retries": 0
        }

        final_state = math_graph.invoke(initial_state)

        # Assert correct transitions and outputs
        self.assertEqual(final_state["question_type"], "ncert_exercise")
        self.assertEqual(final_state["retries"], 1) # incremented on verify
        self.assertTrue(final_state["is_correct"])
        self.assertEqual(final_state["final_answer"], "Solution: 4.")
        
        # Verify node calls
        mock_planner.plan.assert_called_once()
        mock_solver.retrieve_context.assert_called_once()
        mock_memory_agent.retrieve.assert_called_once()
        mock_solver.solve.assert_called_once()
        mock_verifier.verify.assert_called_once()
        mock_formatter.format.assert_called_once()

    @patch("backend.src.graph.nodes.nodes._get_agent")
    @patch("backend.src.graph.nodes.nodes.FirestoreChatMemory")
    def test_graph_retry_loop(
        self, mock_memory_cls, mock_get_agent
    ):
        """Test the graph retrying when verification fails."""
        # Setup mock agents
        mock_planner = MagicMock()
        mock_planner.plan.return_value = {"type": "concept", "class": 10}
        
        mock_solver = MagicMock()
        mock_solver.retrieve_context.return_value = "Rag context"
        mock_solver.solve.return_value = "Solution is 5."
        
        mock_memory_agent = MagicMock()
        mock_memory_agent.retrieve.return_value = {"history": "history", "weak_topics": []}
        
        mock_verifier = MagicMock()
        mock_verifier.verify.side_effect = [
            {"is_correct": False, "feedback": "Math error."},
            {"is_correct": True, "feedback": "Looks good."}
        ]
        
        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Solution: 4."
        
        def side_effect(agent_cls, name):
            if name == "planner": return mock_planner
            if name == "solver": return mock_solver
            if name == "memory": return mock_memory_agent
            if name == "verifier": return mock_verifier
            if name == "formatter": return mock_formatter
            
        mock_get_agent.side_effect = side_effect

        initial_state = {
            "user_query": "What is 2+2?",
            "uid": "test_uid",
            "session_id": "test_session",
            "retries": 0
        }

        final_state = math_graph.invoke(initial_state)

        self.assertEqual(final_state["retries"], 2) # Incremented twice
        self.assertTrue(final_state["is_correct"])
        
        # Verify solver and verifier were called twice
        self.assertEqual(mock_solver.solve.call_count, 2)
        self.assertEqual(mock_verifier.verify.call_count, 2)
        mock_formatter.format.assert_called_once()

if __name__ == "__main__":
    unittest.main()
