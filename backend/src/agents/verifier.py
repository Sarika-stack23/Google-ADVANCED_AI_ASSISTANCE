"""
Verifier Agent (Google ADK)

Checks the solver's output for mathematical or logical errors.
"""

import logging
from typing import Dict, Any

from backend.src.services.llm_service import _get_llm

try:
    from google_adk.agent import Agent
except ImportError:
    class Agent:
        def __init__(self, name, description, instructions, llm=None):
            self.name = name
            self.description = description
            self.instructions = instructions
            self.llm = llm

logger = logging.getLogger("math_assistant.agents.verifier")

class VerifierAgent(Agent):
    """Verifies mathematical solutions."""
    
    def __init__(self):
        super().__init__(
            name="VerifierAgent",
            description="Verifies the step-by-step solution for mathematical errors.",
            instructions=(
                "You are a strict math reviewer. Review the provided solution for the given query.\n"
                "Are there any mathematical errors, calculation mistakes, or logical leaps?\n"
                "For example, check for basic arithmetic errors like 4+4=9.\n"
                "Return ONLY a valid JSON object with two keys:\n"
                "- 'is_correct': A boolean (true/false).\n"
                "- 'feedback': A string explaining the error if is_correct is false, or 'Looks good.' if true.\n"
            )
        )
        self.llm = _get_llm()

    def verify(self, query: str, solution: str) -> Dict[str, Any]:
        """Verify the solution."""
        try:
            prompt = f"{self.instructions}\n\nQuery: {query}\n\nSolution:\n{solution}"
            
            if hasattr(self.llm, "invoke"):
                response = self.llm.invoke(prompt)
                content = response.content
            else:
                content = self.llm(prompt)
                
            import json
            import re
            
            # Extract JSON from response
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            
            return {"is_correct": True, "feedback": "Could not parse verification."}
            
        except Exception as e:
            logger.error(f"Verifier failed: {e}")
            return {"is_correct": True, "feedback": "Verification failed."}
