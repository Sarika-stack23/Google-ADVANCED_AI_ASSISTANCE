"""
Chat API — /api/v1/chat endpoint for math question answering.

Provides a non-streaming POST endpoint that processes math queries
through the MathAIEngine (RAG + symbolic math + LLM with fallback).
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.src.services.llm_service import MathAIEngine
from backend.src.services.vector_service import build_pipeline
from backend.src.services.gemini_service import GeminiVisionService
from backend.src.config import settings
from backend.src.api.middleware.auth import verify_firebase_token
from backend.src.api.limiter import limiter
from backend.src.agents.orchestrator import ADKOrchestrator
from backend.src.graph.math_graph import math_graph

logger = logging.getLogger("math_assistant.api.chat")

router = APIRouter(prefix="/api/v1", tags=["chat"])


# ── Request / Response Models ──────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    query: str = Field(..., min_length=1, max_length=2000, description="Math question to solve")
    session_id: str = Field(default="default", description="Session ID for chat history")
    class_level: Optional[str] = Field(default=None, description="Student class level (e.g., '10', 'JEE')")


class ChatResponse(BaseModel):
    """Response body from the chat endpoint."""
    answer: str
    sources: list = []
    symbolic_hint: Optional[str] = None
    session_id: str
    context_docs: int = 0


class HistoryResponse(BaseModel):
    """Response body for chat history endpoint."""
    session_id: str
    messages: list


class VisionResponse(BaseModel):
    """Response body for the vision extraction endpoint."""
    extracted_math: str
    solution: Optional[str] = None


# ── Endpoints ──────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, payload: ChatRequest, uid: str = Depends(verify_firebase_token)):
    """Process a math question and return a step-by-step solution.

    The query flows through:
    1. Symbolic math verification (SymPy)
    2. Vector store retrieval (ChromaDB/FAISS)
    3. Chat history injection
    4. LLM call with automatic model fallback
    """
    try:
        if getattr(settings, "use_langgraph", False):
            # Phase 5: LangGraph Path
            initial_state = {
                "user_query": payload.query,
                "uid": uid,
                "session_id": payload.session_id,
                "retries": 0
            }
            final_state = math_graph.invoke(initial_state)
            return ChatResponse(
                answer=final_state.get("final_answer", "Error generating response."),
                session_id=payload.session_id,
                is_adk=True
            )
        elif settings.use_adk:
            # Phase 4: ADK Orchestrator Path
            orchestrator = ADKOrchestrator(uid=uid, session_id=payload.session_id)
            result = orchestrator.query(payload.query)
            return ChatResponse(**result)
        else:
            # Legacy Phase 2/3 path
            store = build_pipeline()
            engine = MathAIEngine(vector_store=store, session_id=payload.session_id)
            engine.memory.uid = uid
            result = engine.query(payload.query)
            return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
@limiter.limit("20/minute")
async def chat_stream(request: Request, payload: ChatRequest, uid: str = Depends(verify_firebase_token)):
    """Stream a math solution token-by-token using SSE.
    
    Requires USE_GEMINI=true to function correctly.
    """
    if not settings.use_gemini:
        raise HTTPException(status_code=400, detail="Streaming requires Gemini API to be enabled.")

    from backend.src.services.gemini_service import GeminiService
    from backend.src.services.memory_service import MongoDBChatMemory

    try:
        # We manually orchestrate the context retrieval for streaming
        store = build_pipeline()
        engine = MathAIEngine(vector_store=store, session_id=payload.session_id)
        engine.memory.uid = uid
        
        # 1. Get context and history
        source_docs, context = engine._retrieve_context(payload.query)
        chat_history = engine.memory.get_langchain_messages(limit=4)
        engine.memory.add_message("human", payload.query)

        gemini = GeminiService()

        import json
        async def generate():
            full_response = ""
            try:
                async for chunk in gemini.stream(payload.query, context=context, chat_history=chat_history):
                    full_response += chunk
                    # Format as SSE
                    yield f"data: {json.dumps({'content': chunk, 'type': 'token'})}\n\n"
                
                # Save full response to memory after streaming completes
                engine.memory.add_message("assistant", full_response)
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: {json.dumps({'content': f'\\n\\n⚠️ Streaming error: {e}', 'type': 'token'})}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Chat stream endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/extract", response_model=VisionResponse)
@limiter.limit("20/minute")
async def extract_math_from_image(request: Request, file: UploadFile = File(...), solve: bool = Form(False), uid: str = Depends(verify_firebase_token)):
    """Extract math from an uploaded image using Gemini Vision."""
    if not settings.use_gemini:
        raise HTTPException(status_code=400, detail="Vision extraction requires Gemini API.")

    try:
        image_bytes = await file.read()
        vision_service = GeminiVisionService()
        
        if solve:
            result = vision_service.extract_and_solve(image_bytes, mime_type=file.content_type)
            return VisionResponse(
                extracted_math=result["extracted"],
                solution=result["solution"]
            )
        else:
            extracted = vision_service.extract_math_from_image(image_bytes, mime_type=file.content_type)
            return VisionResponse(extracted_math=extracted)
            
    except Exception as e:
        logger.error(f"Vision endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str, uid: str = Depends(verify_firebase_token)):
    """Get chat history for a given session."""
    try:
        engine = MathAIEngine(session_id=session_id)
        engine.memory.uid = uid
        history = engine.get_history()
        # Convert MongoDB ObjectId to string for JSON serialization
        messages = []
        for msg in history:
            messages.append({
                "role": msg.get("role", "unknown"),
                "content": msg.get("content", ""),
                "timestamp": str(msg.get("timestamp", "")),
            })
        return HistoryResponse(session_id=session_id, messages=messages)
    except Exception as e:
        logger.error(f"History endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{session_id}")
async def clear_history(session_id: str, uid: str = Depends(verify_firebase_token)):
    """Clear chat history for a given session."""
    try:
        engine = MathAIEngine(session_id=session_id)
        engine.memory.uid = uid
        engine.clear_memory()
        return {"status": "ok", "message": f"History cleared for session {session_id}"}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
