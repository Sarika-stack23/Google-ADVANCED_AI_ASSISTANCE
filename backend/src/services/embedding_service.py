"""
Embedding Service — Manages dense and sparse embedding models.
"""

import logging
from backend.src.config import settings

logger = logging.getLogger("math_assistant.embeddings")

_DENSE_EMBEDDINGS_CACHE = None

def get_dense_embeddings():
    """Get or create the singleton dense embedding model (text-embedding-004)."""
    global _DENSE_EMBEDDINGS_CACHE
    if _DENSE_EMBEDDINGS_CACHE is None:
        try:
            # First try new gemini integration
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            logger.info("Loading dense embedding model: text-embedding-004")
            _DENSE_EMBEDDINGS_CACHE = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                task_type="retrieval_document"
            )
        except Exception as e:
            logger.warning(f"Failed to load Google embeddings ({e}), falling back to HuggingFace")
            from langchain_huggingface import HuggingFaceEmbeddings
            _DENSE_EMBEDDINGS_CACHE = HuggingFaceEmbeddings(
                model_name=settings.embedding_model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
    return _DENSE_EMBEDDINGS_CACHE
