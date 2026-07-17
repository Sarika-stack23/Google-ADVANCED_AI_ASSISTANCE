"""
MathGraph Definition

Builds the StateGraph and connects nodes with conditional routing.
"""

import logging
from langgraph.graph import StateGraph, START, END

from backend.src.graph.state import MathAgentState
from backend.src.graph.nodes.nodes import (
    classify_node,
    retrieve_rag_node,
    retrieve_memory_node,
    solve_node,
    verify_node,
    format_node
)

logger = logging.getLogger("math_assistant.graph.math_graph")

def should_retry(state: MathAgentState):
    """Conditional edge logic after verification."""
    if state["is_correct"]:
        return "format"
    elif state["retries"] >= 2:
        logger.warning(f"Max retries reached. Forcing format. Feedback: {state.get('verification_feedback')}")
        return "format"
    else:
        logger.info(f"Verification failed. Retrying solve... (Retry {state['retries']})")
        return "solve"

# 1. Initialize StateGraph
graph_builder = StateGraph(MathAgentState)

# 2. Add Nodes
graph_builder.add_node("classify", classify_node)
graph_builder.add_node("retrieve_rag", retrieve_rag_node)
graph_builder.add_node("retrieve_memory", retrieve_memory_node)
graph_builder.add_node("solve", solve_node)
graph_builder.add_node("verify", verify_node)
graph_builder.add_node("format", format_node)

# 3. Add Edges
# Start -> Classify
graph_builder.add_edge(START, "classify")

# Classify -> Parallel Retrievals
graph_builder.add_edge("classify", "retrieve_rag")
graph_builder.add_edge("classify", "retrieve_memory")

# Parallel Retrievals -> Solve
# LangGraph waits for all incoming edges to complete before firing 'solve'
graph_builder.add_edge("retrieve_rag", "solve")
graph_builder.add_edge("retrieve_memory", "solve")

# Solve -> Verify
graph_builder.add_edge("solve", "verify")

# Verify -> Conditional Routing
graph_builder.add_conditional_edges(
    "verify",
    should_retry,
    {
        "format": "format",
        "solve": "solve"
    }
)

# Format -> End
graph_builder.add_edge("format", END)

# 4. Compile Graph
math_graph = graph_builder.compile()
