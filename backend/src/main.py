"""
FastAPI Application — Advanced Mathematics Assistant Backend.

This is the main entry point for the backend API server.
Run with: uvicorn backend.src.main:app --host 0.0.0.0 --port 8080
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.config import settings
from backend.src.services.firebase_service import init_firebase
from backend.src.api.v1 import chat
from backend.src.api.v1 import progress
from backend.src.api.v1 import documents
from backend.src.api.v1 import symbolic

# ── Logging Setup ──────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("math_assistant.app")


# ── Application Lifespan ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI application."""
    logger.info("🚀 Starting Advanced Mathematics Assistant API...")
    logger.info(f"   Environment: {settings.environment}")
    logger.info(f"   LLM Model: {settings.llm_model}")
    logger.info(f"   Vector DB: {settings.vector_db_type}")

    # Initialize Firebase Admin SDK
    init_firebase()

    # Pre-build knowledge base on startup (optional, lazy by default)
    # Uncomment the following to eagerly build on startup:
    # from backend.src.services.vector_service import build_pipeline
    # build_pipeline()

    yield  # Application is running

    logger.info("🛑 Shutting down Advanced Mathematics Assistant API.")


# ── FastAPI App ────────────────────────────────────────────────────────
app = FastAPI(
    title="Advanced Mathematics Assistant API",
    description=(
        "AI-powered math tutoring API for Indian school students (Class 6-12 + JEE). "
        "Uses RAG retrieval, SymPy symbolic computation, and LLM-based step-by-step solutions."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

from backend.src.api.limiter import limiter, _rate_limit_exceeded_handler, RateLimitExceeded
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── CORS Middleware ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "http://localhost:8501",      # Streamlit
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(progress.router)
app.include_router(documents.router)
app.include_router(symbolic.router)

from backend.src.api.v1 import quiz
app.include_router(quiz.router, prefix="/api/v1/quiz", tags=["Quiz"])

@app.get("/health")
async def health_check():
    """Health check endpoint — returns API status and knowledge base info.

    Returns HTTP 200 with:
    - status: "ok"
    - environment: current environment
    - kb_docs: number of indexed knowledge base documents (0 if not yet built)
    """
    kb_docs = 0
    try:
        from backend.src.services.vector_service import _PIPELINE_CACHE
        store = _PIPELINE_CACHE.get("store")
        if store:
            kb_docs = store.get_document_count()
    except Exception:
        pass

    return {
        "status": "ok",
        "environment": settings.environment,
        "version": "1.0.0",
        "kb_docs": kb_docs,
        "llm_model": settings.llm_model,
        "vector_db": settings.vector_db_type,
    }


@app.get("/")
async def root():
    """Root endpoint — redirect info."""
    return {
        "message": "Advanced Mathematics Assistant API",
        "docs": "/docs",
        "health": "/health",
    }
