"""
Vector Store Service — ChromaDB/FAISS vector database operations.

Extracted from main.py L276-L397. Manages embedding model loading,
vector store creation/loading, similarity search, and the full
knowledge base build pipeline.
"""

import logging
from pathlib import Path
from typing import Optional, List

from backend.src.config import settings

logger = logging.getLogger("math_assistant.vector")

_EMBEDDINGS_CACHE = {}


def get_embeddings():
    """Get or create the singleton embedding model instance."""
    if "model" not in _EMBEDDINGS_CACHE:
        from langchain_huggingface import HuggingFaceEmbeddings
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _EMBEDDINGS_CACHE["model"] = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _EMBEDDINGS_CACHE["model"]


class MathVectorStore:
    """Vector store abstraction supporting ChromaDB (primary) and FAISS (fallback)."""

    def __init__(self):
        self.embeddings = get_embeddings()
        self.vectorstore = None
        self.db_type = settings.vector_db_type
        self._load_existing()

    def _load_existing(self):
        if self.db_type == "chroma":
            self._try_chroma()
        else:
            self._try_faiss()

    def _try_chroma(self, documents=None):
        try:
            from langchain_community.vectorstores import Chroma
            persist_path = Path(settings.chroma_persist_dir)
            persist_path.mkdir(parents=True, exist_ok=True)
            if documents:
                self.vectorstore = Chroma.from_documents(
                    documents=documents, embedding=self.embeddings,
                    collection_name=settings.collection_name,
                    persist_directory=str(persist_path))
                logger.info("ChromaDB created.")
            elif list(persist_path.glob("*.sqlite3")):
                self.vectorstore = Chroma(
                    collection_name=settings.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(persist_path))
                logger.info(f"ChromaDB loaded ({self.vectorstore._collection.count()} docs)")
        except Exception as e:
            logger.warning(f"ChromaDB failed ({type(e).__name__}: {e}), switching to FAISS")
            self.db_type = "faiss"
            if documents:
                self._try_faiss(documents)

    def _try_faiss(self, documents=None):
        try:
            from langchain_community.vectorstores import FAISS
            index_path = Path(settings.faiss_index_path)
            if documents:
                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
                index_path.mkdir(parents=True, exist_ok=True)
                self.vectorstore.save_local(str(index_path))
                logger.info(f"FAISS saved to {index_path}")
            elif index_path.exists() and any(index_path.iterdir()):
                self.vectorstore = FAISS.load_local(
                    str(index_path), self.embeddings,
                    allow_dangerous_deserialization=True)
                logger.info("FAISS loaded.")
        except Exception as e:
            logger.error(f"FAISS failed: {e}")

    def build_knowledge_base(self, documents):
        """Build the vector index from a list of Document chunks."""
        logger.info(f"Building knowledge base with {len(documents)} chunks...")
        if self.db_type == "chroma":
            self._try_chroma(documents)
        else:
            self._try_faiss(documents)
        logger.info("Knowledge base ready.")

    def add_documents(self, documents):
        """Add documents to an existing vector store, or create one."""
        if self.vectorstore is None:
            self.build_knowledge_base(documents)
        else:
            self.vectorstore.add_documents(documents)

    def similarity_search(self, query: str, k: int = None, filter_topic: str = None):
        """Search for similar documents by query string."""
        k = k or settings.top_k_results
        if self.vectorstore is None:
            return []
        try:
            if filter_topic and self.db_type == "chroma":
                return self.vectorstore.similarity_search(query, k=k, filter={"topic": filter_topic})
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def as_retriever(self, k: int = None):
        """Return a LangChain retriever interface."""
        k = k or settings.top_k_results
        return self.vectorstore.as_retriever(search_kwargs={"k": k}) if self.vectorstore else None

    def get_document_count(self) -> int:
        """Get the number of indexed documents."""
        if self.vectorstore is None:
            return 0
        try:
            return (self.vectorstore._collection.count() if self.db_type == "chroma"
                    else self.vectorstore.index.ntotal)
        except Exception as e:
            logger.error(f"get_document_count failed: {e}")
            return 0

    def is_ready(self) -> bool:
        """Check if the vector store is loaded and has documents."""
        return self.vectorstore is not None and self.get_document_count() > 0


_PIPELINE_CACHE = {}


def build_pipeline(pdf_paths=None, urls=None, text_paths=None, force_rebuild=False) -> MathVectorStore:
    """Build or load the full knowledge base pipeline (cached per process)."""
    from backend.src.math.knowledge_indexer import MathDataLoader, MathDataPreprocessor, MathTextSplitter

    if "store" in _PIPELINE_CACHE and not force_rebuild:
        return _PIPELINE_CACHE["store"]
    store = MathVectorStore()
    if store.is_ready() and not force_rebuild:
        logger.info(f"Knowledge base already built ({store.get_document_count()} docs).")
        _PIPELINE_CACHE["store"] = store
        return store
    raw_docs   = MathDataLoader().load_all(pdf_paths=pdf_paths or [], urls=urls or [], text_paths=text_paths or [])
    clean_docs = MathDataPreprocessor().preprocess_documents(raw_docs)
    chunks     = MathTextSplitter().split_documents(clean_docs)
    store.build_knowledge_base(chunks)
    _PIPELINE_CACHE["store"] = store
    return store
