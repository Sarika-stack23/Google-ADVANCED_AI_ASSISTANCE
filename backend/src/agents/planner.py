"""
Planner Agent (Google ADK)

Responsible for classifying the incoming query into a problem type and 
target educational class.
"""

import logging
from typing import Dict, Any

from backend.src.services.llm_service import _get_llm
from backend.src.config import settings

try:
    from google_adk.agent import Agent
except ImportError:
    # Mock fallback for test environment if ADK is missing
    class Agent:
        def __init__(self, name, description, instructions, llm=None):
            self.name = name
            self.description = description
            self.instructions = instructions
            self.llm = llm
            
logger = logging.getLogger("math_assistant.agents.planner")

class PlannerAgent(Agent):
    """Classifies math problems into type and class level."""
    
    def __init__(self):
        super().__init__(
            name="PlannerAgent",
            description="Analyzes mathematical queries to classify them by type and class level.",
            instructions=(
                "You are an expert curriculum analyzer. Your job is to classify the given "
                "mathematical query.\n"
                "Return ONLY a valid JSON object with two keys:\n"
                "- 'type': A string representing the question type (e.g., 'ncert_exercise', 'concept_explanation', 'jee_advanced').\n"
                "- 'class': An integer representing the target class level (e.g., 6, 8, 10, 11, 12). If unknown, use 10.\n"
                "Example output: {\"type\": \"ncert_exercise\", \"class\": 10}"
            )
        )
        self.llm = _get_llm()

    def plan(self, query: str) -> Dict[str, Any]:
        """Classify the query."""
        try:
            # Simple invocation of LLM for the agent
            if hasattr(self.llm, "invoke"):
                response = self.llm.invoke(f"{self.instructions}\n\nQuery: {query}")
                content = response.content
            else:
                content = self.llm(f"{self.instructions}\n\nQuery: {query}")
            
            import json
            import re
            
            # Extract JSON from response
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            
            return {"type": "unknown", "class": 10}
            
        except Exception as e:
            logger.error(f"Planner failed: {e}")
            return {"type": "unknown", "class": 10}
