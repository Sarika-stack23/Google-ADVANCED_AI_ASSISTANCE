"""
ADK Orchestrator

Chains the 5 agents together (Planner -> Memory -> Solver -> Verifier -> Formatter).
Replaces the monolithic MathAIEngine.
"""

import logging
from typing import Dict, Any

from backend.src.agents.planner import PlannerAgent
from backend.src.agents.memory import MemoryAgent
from backend.src.agents.solver import SolverAgent
from backend.src.agents.verifier import VerifierAgent
from backend.src.agents.formatter import FormatterAgent

logger = logging.getLogger("math_assistant.agents.orchestrator")

class ADKOrchestrator:
    """Orchestrates the multi-agent ADK pipeline."""
    
    def __init__(self, uid: str, session_id: str):
        self.uid = uid
        self.session_id = session_id
        
        self.planner = PlannerAgent()
        self.memory = MemoryAgent()
        self.solver = SolverAgent()
        self.verifier = VerifierAgent()
        self.formatter = FormatterAgent()
        
    def query(self, user_query: str) -> Dict[str, Any]:
        """Execute the full agent pipeline."""
        logger.info(f"Starting ADK Orchestrator for session {self.session_id}")
        
        # 1. Plan
        plan = self.planner.plan(user_query)
        logger.info(f"Plan: {plan}")
        class_level = plan.get("class", 10)
        
        # 2. Memory Retrieval
        mem_context = self.memory.retrieve(self.uid, self.session_id)
        
        # 3. Solver + RAG
        rag_context = self.solver.retrieve_context(user_query)
        raw_solution = self.solver.solve(user_query, rag_context, mem_context["history"])
        
        # 4. Verify
        # We allow up to 2 retries on verification failure
        verification = self.verifier.verify(user_query, raw_solution)
        retries = 0
        while not verification.get("is_correct", True) and retries < 2:
            logger.warning(f"Verification failed: {verification.get('feedback')}. Retrying...")
            feedback = verification.get("feedback")
            # Inject feedback into prompt
            refined_query = f"{user_query}\nNote: Your previous attempt had an error: {feedback}. Please fix it."
            raw_solution = self.solver.solve(refined_query, rag_context, mem_context["history"])
            verification = self.verifier.verify(user_query, raw_solution)
            retries += 1
            
        # 5. Format
        final_answer = self.formatter.format(user_query, raw_solution, class_level)
        
        # Save to memory (Memory agent handles retrieval, but we use memory service directly for saving)
        from backend.src.services.memory_service import FirestoreChatMemory
        mem_svc = FirestoreChatMemory(uid=self.uid, session_id=self.session_id)
        mem_svc.add_message("human", user_query)
        mem_svc.add_message("assistant", final_answer)
        
        return {
            "answer": final_answer,
            "session_id": self.session_id,
            "is_adk": True
        }
