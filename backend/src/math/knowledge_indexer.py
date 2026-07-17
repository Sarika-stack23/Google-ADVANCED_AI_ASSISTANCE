"""
Knowledge Base Indexing Pipeline — Markdown loading, preprocessing, and chunking for Qdrant.
"""

import os
import glob
import logging
from typing import List

from langchain_core.documents import Document

from backend.src.services.qdrant_service import QdrantService
from backend.src.config import settings

logger = logging.getLogger("math_assistant.indexer")

class KnowledgeIndexer:
    """Parses local markdown files and indexes them into the Qdrant vector store."""
    
    def __init__(self, kb_dir: str = "knowledge-base"):
        self.kb_dir = kb_dir
        self.qdrant = QdrantService()

    def parse_frontmatter(self, text: str) -> tuple[dict, str]:
        """Extract metadata from markdown frontmatter."""
        metadata = {}
        content = text
        if text.startswith("---\n"):
            parts = text.split("---\n", 2)
            if len(parts) == 3:
                frontmatter = parts[1]
                content = parts[2]
                for line in frontmatter.strip().split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        metadata[key.strip()] = val.strip()
        return metadata, content.strip()

    def load_markdown_files(self) -> List[Document]:
        """Load all markdown files from the knowledge base directory."""
        documents = []
        search_pattern = os.path.join(self.kb_dir, "**", "*.md")
        filepaths = glob.glob(search_pattern, recursive=True)
        
        logger.info(f"Found {len(filepaths)} markdown files in {self.kb_dir}")
        
        for filepath in filepaths:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                    
                metadata, content = self.parse_frontmatter(text)
                metadata["source_file"] = filepath
                
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to process {filepath}: {e}")
                
        return documents

    def index_all(self):
        """Load all files, split, and index into Qdrant."""
        logger.info("Starting Knowledge Base indexing...")
        docs = self.load_markdown_files()
        if not docs:
            logger.warning("No documents found to index.")
            return

        from langchain.text_splitter import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
            
        logger.info(f"Created {len(chunks)} chunks. Pushing to Qdrant...")
        self.qdrant.add_documents(chunks)
        logger.info(f"Indexing complete. Total vectors: {self.qdrant.get_document_count()}")

if __name__ == "__main__":
    indexer = KnowledgeIndexer()
    indexer.index_all()
