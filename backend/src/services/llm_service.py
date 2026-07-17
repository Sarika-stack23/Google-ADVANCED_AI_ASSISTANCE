"""
LLM Service — Gemini (primary) + Groq (fallback) orchestrator.

Phase 2: Gemini Integration.
- When USE_GEMINI=true (default), queries go through GeminiService.
- When USE_GEMINI=false or GEMINI_API_KEY is missing, falls back to Groq.
- _get_llm: Groq LLM factory (preserved for fallback)
- MathAIEngine: Orchestrates retrieval, symbolic math, and LLM calls.
"""

import re
import time
import logging
from typing import Dict, Any, Optional, Tuple

from backend.src.config import settings, SYSTEM_TEMPLATE
from backend.src.math.symbolic_engine import SymbolicMathEngine
from backend.src.services.memory_service import MongoDBChatMemory

try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
except ImportError:
    from langchain.schema import HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger("math_assistant.llm")

_LLM_CACHE = {}


def _get_llm(model=None):
    """Get or create a cached Groq LLM instance for a given model name."""
    key = model or settings.groq_model_fallbacks[0]
    if key not in _LLM_CACHE:
        from langchain_groq import ChatGroq
        api_key = settings.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY not set. Add it to your .env file.")
        logger.info(f"Initializing Groq LLM: {key}")
        _LLM_CACHE[key] = ChatGroq(
            groq_api_key=api_key,
            model_name=key,
            temperature=0.1,
            max_tokens=2048,
        )
    return _LLM_CACHE[key]


class MathAIEngine:
    """Orchestrates RAG retrieval, symbolic math, and LLM calls for math tutoring."""

    def __init__(self, vector_store=None, session_id: str = "default"):
        self.llm          = self._init_llm()
        self.vector_store = vector_store
        self.memory       = MongoDBChatMemory(session_id=session_id)
        self.symbolic     = SymbolicMathEngine()
        self.session_id   = session_id

    def _init_llm(self):
        """Initialize the primary LLM model."""
        return _get_llm(settings.groq_model_fallbacks[0])

    def _retrieve_context(self, query: str) -> Tuple[list, str]:
        """Retrieve relevant documents from the vector store."""
        if not self.vector_store or not self.vector_store.is_ready():
            return [], "No knowledge base available. Using general mathematical knowledge."
        docs = self.vector_store.similarity_search(query, k=3)
        if not docs:
            return [], "No specific context found."
        parts = [f"[Reference {i+1} - {d.metadata.get('topic','math')}]\n{d.page_content}"
                 for i, d in enumerate(docs)]
        return docs, "\n\n---\n\n".join(parts)

    def _symbolic_hint(self, query: str) -> Optional[str]:
        """Try to get a symbolic verification hint for the query."""
        ql = query.lower()
        for pattern, action in [
            (r"(?:differentiate|derivative of|d/dx)\s+(.+?)(?:\s+with respect|\s*$)", "diff"),
            (r"(?:integrate|integral of)\s+(.+?)(?:\s+with respect|\s+dx|\s*$)", "int"),
            (r"solve\s+(.+?)\s+(?:for|=)", "solve"),
        ]:
            m = re.search(pattern, ql)
            if m:
                expr = m.group(1).strip()
                result = (self.symbolic.differentiate(expr) if action == "diff"
                          else self.symbolic.integrate(expr) if action == "int"
                          else self.symbolic.solve_equation(expr))
                if result:
                    return f"[Symbolic verification: {result}]"
        return None

    def query(self, user_input: str) -> Dict[str, Any]:
        """Process a user math query through the full RAG pipeline.

        Flow: symbolic hint → vector retrieval → chat history →
              Gemini (primary) or Groq (fallback) → store response.
        """
        hint        = self._symbolic_hint(user_input)
        source_docs, context = self._retrieve_context(user_input)
        chat_history = self.memory.get_langchain_messages(limit=4)

        # Store human message BEFORE LLM call so history order is correct
        self.memory.add_message("human", user_input)

        # ── Try Gemini first (Phase 2) ─────────────────────────────────
        if settings.use_gemini and settings.gemini_api_key:
            try:
                from backend.src.services.gemini_service import GeminiService
                gemini = GeminiService()
                answer = gemini.query(user_input, context=context, chat_history=chat_history)
                if answer and not answer.startswith("⚠️"):
                    self.memory.add_message("assistant", answer)
                    sources = [{"topic": d.metadata.get("topic", "unknown"),
                                "source": d.metadata.get("source", "kb"),
                                "difficulty": d.metadata.get("difficulty", "unknown")}
                               for d in source_docs]
                    return {"answer": answer, "sources": sources, "symbolic_hint": hint,
                            "session_id": self.session_id, "context_docs": len(source_docs)}
            except Exception as e:
                logger.warning(f"Gemini failed, falling back to Groq: {e}")

        # ── Groq Fallback ──────────────────────────────────────────────
        # Build messages list manually — NEVER pass math content through
        # LangChain format_messages(), because curly braces in math break templates
        system_text = SYSTEM_TEMPLATE.replace("{context}", context)
        llm_messages = [SystemMessage(content=system_text)]
        for msg in chat_history:
            llm_messages.append(msg)
        llm_messages.append(HumanMessage(content=user_input))

        # Auto-retry with model fallback
        answer      = None
        last_error  = None
        used_models = []
        for model_name in settings.groq_model_fallbacks:
            if model_name in used_models:
                continue
            used_models.append(model_name)
            llm = _get_llm(model_name)
            for _attempt in range(2):
                try:
                    raw = llm.invoke(llm_messages).content
                    if raw and not any(p in raw.lower() for p in
                                       ["rate limit", "too many requests", "service unavailable"]):
                        answer = raw
                        if model_name != settings.groq_model_fallbacks[0]:
                            answer = f"*(Using fallback model: {model_name})*\n\n" + answer
                        break
                    else:
                        raise Exception(raw or "Empty response")
                except Exception as e:
                    last_error = e
                    err = str(e).lower()
                    full_err = str(e)
                    logger.warning(f"Model {model_name} attempt {_attempt+1} failed: {e}")
                    if "per day" in full_err or "tokens per day" in full_err:
                        logger.info(f"Daily limit on {model_name}, trying next model...")
                        break
                    elif "429" in full_err or "rate_limit" in err:
                        time.sleep(2 ** _attempt)
                        continue
                    elif "timeout" in err or "connect" in err or "503" in err:
                        time.sleep(1)
                        continue
                    else:
                        break
            if answer:
                break

        if answer is None:
            full_err = str(last_error)
            err      = full_err.lower()
            logger.error(f"LLM failed: [{type(last_error).__name__}] {full_err}")

            if "401" in full_err or "invalid_api_key" in err:
                answer = "⚠️ Invalid API key. Check GROQ_API_KEY in your .env file."
            elif "429" in full_err or "rate_limit_exceeded" in err:
                retry_match = re.search(r'try again in (.+?)\.', full_err)
                retry_info  = f" Groq says: try again in **{retry_match.group(1)}**." if retry_match else ""
                if "per day" in full_err or "tokens per day" in full_err or "TPD" in full_err:
                    answer = (f"⚠️ **Daily token limit reached** (Groq free tier: 100,000 tokens/day).{retry_info}\n\n"
                              f"To keep using the app now, change your `.env`:\n```\nLLM_MODEL=llama3-8b-8192\n```\n"
                              f"Then restart Streamlit. The 8B model has a separate 500k/day quota.")
                else:
                    answer = f"⚠️ **Rate limit hit** (too many requests per minute).{retry_info} Wait 20–30 seconds and try again."
            elif "context_length" in err or ("context" in err and "length" in err):
                answer = "⚠️ Question + context too long. Try a shorter question."
            elif "connect" in err or "connection" in err:
                answer = "⚠️ Cannot reach Groq API. Check your internet connection."
            elif "timeout" in err:
                answer = "⚠️ Request timed out. Try again."
            else:
                answer = f"⚠️ Error ({type(last_error).__name__}): {full_err}"

        self.memory.add_message("assistant", answer)

        sources = [{"topic":      d.metadata.get("topic", "unknown"),
                    "source":     d.metadata.get("source", "kb"),
                    "difficulty": d.metadata.get("difficulty", "unknown")}
                   for d in source_docs]

        return {"answer": answer, "sources": sources, "symbolic_hint": hint,
                "session_id": self.session_id, "context_docs": len(source_docs)}

    def clear_memory(self):
        """Clear chat history for this session."""
        self.memory.clear_history()

    def get_history(self):
        """Get full chat history for this session."""
        return self.memory.get_history(limit=50)
