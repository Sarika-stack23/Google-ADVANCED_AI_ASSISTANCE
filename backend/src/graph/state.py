"""
LangGraph State Definition
"""

from typing import TypedDict, Annotated, List

class MathAgentState(TypedDict):
    """Represents the state of the math orchestration pipeline."""
    
    # Input
    user_query: str
    uid: str
    session_id: str
    
    # Planner output
    question_type: str
    class_level: int
    
    # Retrievals (Running in parallel)
    rag_context: str
    history: str
    weak_topics: List[str]
    
    # Solver Output
    raw_solution: str
    
    # Verifier Feedback
    is_correct: bool
    verification_feedback: str
    retries: int
    
    # Formatter Output
    final_answer: str
