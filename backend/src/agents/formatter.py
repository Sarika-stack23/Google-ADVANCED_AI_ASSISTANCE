"""
Formatter Agent (Google ADK)

Formats the final verified solution according to the SYSTEM_TEMPLATE constraints
(e.g., emojis, teacher reactions, LaTeX math mode).
"""

import logging
from backend.src.services.llm_service import _get_llm
from backend.src.config import SYSTEM_TEMPLATE

try:
    from google_adk.agent import Agent
except ImportError:
    class Agent:
        def __init__(self, name, description, instructions, llm=None):
            self.name = name
            self.description = description
            self.instructions = instructions
            self.llm = llm

logger = logging.getLogger("math_assistant.agents.formatter")

class FormatterAgent(Agent):
    """Formats the solution."""
    
    def __init__(self):
        super().__init__(
            name="FormatterAgent",
            description="Formats the mathematical solution based on strict system templates.",
            instructions=(
                f"{SYSTEM_TEMPLATE}\n\n"
                "Your task is to take the provided raw mathematical solution and rewrite it "
                "to strictly adhere to the above formatting rules, including LaTeX math mode, "
                "teacher reactions, and class-level appropriate depth."
            )
        )
        self.llm = _get_llm()

    def format(self, query: str, raw_solution: str, class_level: int) -> str:
        """Format the solution."""
        try:
            prompt = (
                f"{self.instructions}\n\n"
                f"Target Class Level: {class_level}\n\n"
                f"Original Query: {query}\n\n"
                f"Raw Solution to Format:\n{raw_solution}"
            )
            
            if hasattr(self.llm, "invoke"):
                response = self.llm.invoke(prompt)
                return response.content
            else:
                return self.llm(prompt)
                
        except Exception as e:
            logger.error(f"Formatter failed: {e}")
            return raw_solution
