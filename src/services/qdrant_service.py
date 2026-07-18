"""
Qdrant Vector Service — Hybrid Search (Dense + Sparse).
"""

import logging
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse

from backend.src.config import settings
from backend.src.services.embedding_service import get_dense_embeddings

logger = logging.getLogger("math_assistant.qdrant")

class QdrantService:
    """Manages the Qdrant Cloud or local vector store with Hybrid Search."""

    def __init__(self):
        self.collection_name = settings.collection_name
        self.url = getattr(settings, "qdrant_url", ":memory:")
        self.api_key = getattr(settings, "qdrant_api_key", "")
        
        logger.info(f"Initializing Qdrant at {self.url}")
        
        # 1. Initialize Client
        if self.url == ":memory:":
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key if self.api_key else None
            )
            
        # 2. Get dense embeddings
        self.dense_embeddings = get_dense_embeddings()
        
        # 3. Setup sparse embeddings for hybrid search
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        
        # 4. Create collection if not exists
        if not self.client.collection_exists(self.collection_name):
            from qdrant_client.http import models as rest
            
            # Since we are using Hybrid search (dense + sparse), we need to configure vectors properly.
            # But langchain_qdrant handles the schema if we use `from_texts`/`from_documents`.
            # A safer way to initialize an empty hybrid store is to let langchain_qdrant handle it:
            # We can just skip manual creation and let `add_documents` handle it, but `QdrantVectorStore` 
            # init requires the collection to exist if we pass `client`.
            
            # Let's create it with the correct dimensions for HuggingFace (384) or Gemini (768).
            # But wait, QdrantVectorStore.from_texts() creates everything automatically.
            pass  # We will defer instantiation if it doesn't exist, or just use from_documents later.
            
        # Actually, LangChain's QdrantVectorStore has a parameter `force_recreate=True/False` or we can just 
        # let `from_texts` do the heavy lifting in `add_documents`.
        # For simplicity, we just initialize it:
        try:
            self.vectorstore = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.dense_embeddings,
                sparse_embedding=self.sparse_embeddings,
                retrieval_mode=RetrievalMode.HYBRID
            )
        except ValueError as e:
            if "not found" in str(e):
                logger.warning(f"Collection {self.collection_name} not found. It will be created upon first insertion.")
                self.vectorstore = None
            else:
                raise e

    def add_documents(self, documents: List[Any]):
        """Index documents into Qdrant."""
        logger.info(f"Indexing {len(documents)} documents into Qdrant...")
        if self.vectorstore is None:
            self.vectorstore = QdrantVectorStore.from_documents(
                documents,
                embedding=self.dense_embeddings,
                sparse_embedding=self.sparse_embeddings,
                location=self.url if self.url == ":memory:" else None,
                url=self.url if self.url != ":memory:" else None,
                api_key=self.api_key if self.api_key and self.url != ":memory:" else None,
                collection_name=self.collection_name,
                retrieval_mode=RetrievalMode.HYBRID
            )
        else:
            self.vectorstore.add_documents(documents)
        logger.info("Indexing complete.")

    def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        filter_topic: Optional[str] = None,
        filter_class: Optional[str] = None,
        filter_chapter: Optional[str] = None
    ) -> List[Any]:
        """Hybrid search with metadata filtering."""
        
        if not self.vectorstore:
            return []
            
        from qdrant_client.http import models as rest
        
        filter_conditions = []
        if filter_topic:
            filter_conditions.append(rest.FieldCondition(key="topic", match=rest.MatchValue(value=filter_topic)))
        if filter_class:
            filter_conditions.append(rest.FieldCondition(key="class_level", match=rest.MatchValue(value=filter_class)))
        if filter_chapter:
            filter_conditions.append(rest.FieldCondition(key="chapter", match=rest.MatchValue(value=filter_chapter)))
            
        qdrant_filter = rest.Filter(must=filter_conditions) if filter_conditions else None
        
        try:
            return self.vectorstore.similarity_search(
                query=query, 
                k=k, 
                filter=qdrant_filter
            )
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []

    def is_ready(self) -> bool:
        """Check if the vector store is initialized and ready."""
        return self.vectorstore is not None

    def as_retriever(self, k: int = 5, metadata_filters: Dict[str, Any] = None):
        """Return a LangChain retriever interface with dynamic filters."""
        from qdrant_client.http import models as rest
        
        qdrant_filter = None
        if metadata_filters:
            conditions = []
            for key, val in metadata_filters.items():
                conditions.append(rest.FieldCondition(key=key, match=rest.MatchValue(value=val)))
            qdrant_filter = rest.Filter(must=conditions)
            
        search_kwargs = {"k": k}
        if qdrant_filter:
            search_kwargs["filter"] = qdrant_filter
            
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)

    def get_document_count(self) -> int:
        """Count total documents in collection."""
        try:
            return self.client.count(self.collection_name).count
        except Exception:
            return 0
