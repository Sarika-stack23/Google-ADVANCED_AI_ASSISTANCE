"""
LangGraph Nodes

Wraps the ADK agents into functional nodes that mutate the MathAgentState.
"""

import logging
from backend.src.graph.state import MathAgentState
from backend.src.agents.planner import PlannerAgent
from backend.src.agents.memory import MemoryAgent
from backend.src.agents.solver import SolverAgent
from backend.src.agents.verifier import VerifierAgent
from backend.src.agents.formatter import FormatterAgent
from backend.src.services.memory_service import FirestoreChatMemory

logger = logging.getLogger("math_assistant.graph.nodes")

# Lazy initialization of agents
_agents = {}

def _get_agent(agent_class, name):
    if name not in _agents:
        _agents[name] = agent_class()
    return _agents[name]

def classify_node(state: MathAgentState) -> dict:
    """Classify the user query."""
    planner = _get_agent(PlannerAgent, "planner")
    plan = planner.plan(state["user_query"])
    return {
        "question_type": plan.get("type", "unknown"),
        "class_level": plan.get("class", 10),
        "retries": 0  # initialize retries
    }

def retrieve_rag_node(state: MathAgentState) -> dict:
    """Fetch RAG context from the vector store."""
    solver = _get_agent(SolverAgent, "solver")
    context = solver.retrieve_context(state["user_query"])
    return {"rag_context": context}

def retrieve_memory_node(state: MathAgentState) -> dict:
    """Fetch history and weak topics from Firestore."""
    memory = _get_agent(MemoryAgent, "memory")
    mem = memory.retrieve(state["uid"], state["session_id"])
    return {
        "history": mem.get("history", ""),
        "weak_topics": mem.get("weak_topics", [])
    }

def solve_node(state: MathAgentState) -> dict:
    """Generate a solution based on current state context."""
    query = state["user_query"]
    solver = _get_agent(SolverAgent, "solver")
    
    # If this is a retry, append the verifier's feedback
    if state.get("retries", 0) > 0 and state.get("verification_feedback"):
        query = f"{query}\nNote: Your previous attempt failed validation: {state['verification_feedback']}. Fix it."
        
    solution = solver.solve(query, state.get("rag_context", ""), state.get("history", ""))
    return {"raw_solution": solution}

def verify_node(state: MathAgentState) -> dict:
    """Verify the generated solution."""
    verifier = _get_agent(VerifierAgent, "verifier")
    verification = verifier.verify(state["user_query"], state["raw_solution"])
    return {
        "is_correct": verification.get("is_correct", True),
        "verification_feedback": verification.get("feedback", ""),
        "retries": state.get("retries", 0) + 1
    }

def format_node(state: MathAgentState) -> dict:
    """Format the final output and save it to chat history."""
    formatter = _get_agent(FormatterAgent, "formatter")
    final_answer = formatter.format(
        state["user_query"], 
        state["raw_solution"], 
        state.get("class_level", 10)
    )
    
    # Side effect: Save the conversation turn
    mem_svc = FirestoreChatMemory(uid=state["uid"], session_id=state["session_id"])
    mem_svc.add_message("human", state["user_query"])
    mem_svc.add_message("assistant", final_answer)
    
    return {"final_answer": final_answer}
