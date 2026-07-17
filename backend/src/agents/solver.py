"""
Solver Agent (Google ADK)

Uses RAG context and LLM to solve the math problem.
"""

import logging
from typing import Dict, Any, List

from backend.src.services.llm_service import _get_llm
from backend.src.services.vector_service import build_pipeline
from backend.src.config import settings

try:
    from google_adk.agent import Agent
except ImportError:
    class Agent:
        def __init__(self, name, description, instructions, llm=None):
            self.name = name
            self.description = description
            self.instructions = instructions
            self.llm = llm

logger = logging.getLogger("math_assistant.agents.solver")

class SolverAgent(Agent):
    """Core mathematical engine."""
    
    def __init__(self):
        super().__init__(
            name="SolverAgent",
            description="Solves mathematical problems step-by-step using RAG context.",
            instructions="Solve the math problem accurately."
        )
        self.llm = _get_llm()
        self.vector_store = build_pipeline()
        
        from backend.src.agents.mcp_registry import get_mcp_tools
        self.tools = get_mcp_tools()
        
        try:
            from langchain.agents import create_tool_calling_agent, AgentExecutor
            from langchain_core.prompts import ChatPromptTemplate
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an advanced mathematical solver. Provide a clear, step-by-step solution. You MUST use the provided tools for differentiation, integration, arithmetic, python code execution, etc. whenever a complex calculation is needed. Do not guess complex answers."),
                ("human", "Question: {query}\n\nRelevant Knowledge Base Context:\n{context}\n\nPrevious Chat Context:\n{history}\n\nSolution:")
            ])
            
            # If the LLM doesn't support bind_tools, this will fail or we can catch it
            if getattr(settings, "USE_MCP", True) and hasattr(self.llm, "bind_tools") and self.tools:
                agent = create_tool_calling_agent(self.llm, self.tools, prompt)
                self.executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
            else:
                self.executor = None
        except ImportError:
            self.executor = None

    def solve(self, query: str, context: str, history: str) -> str:
        """Generate a solution based on query, RAG context, and history."""
        if getattr(self, 'executor', None):
            try:
                response = self.executor.invoke({
                    "query": query,
                    "context": context,
                    "history": history
                })
                return response.get("output", "")
            except Exception as e:
                logger.error(f"Solver AgentExecutor failed: {e}")
                return "I encountered an error while trying to solve this problem with tools."
        
        prompt = (
            f"You are a mathematical solver. Provide a clear, step-by-step solution.\n\n"
            f"Question: {query}\n\n"
            f"Relevant Knowledge Base Context:\n{context}\n\n"
            f"Previous Chat Context:\n{history}\n\n"
            f"Solution:"
        )
        
        try:
            if hasattr(self.llm, "invoke"):
                response = self.llm.invoke(prompt)
                return response.content
            else:
                return self.llm(prompt)
        except Exception as e:
            logger.error(f"Solver failed: {e}")
            return "I encountered an error while trying to solve this problem."

    def retrieve_context(self, query: str) -> str:
        """Retrieve RAG context for the query."""
        try:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant context found."
            return "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            logger.warning(f"RAG retrieval failed in Solver: {e}")
            return "No relevant context found."
