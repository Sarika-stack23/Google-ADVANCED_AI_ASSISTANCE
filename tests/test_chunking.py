"""Tests for MathTextSplitter — extracted from main.py L2620-L2632.

Validates that large documents are split into chunks and that
metadata is preserved across all resulting chunks.
"""

import unittest
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import MathTextSplitter

try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        class Document:
            def __init__(self, page_content: str, metadata: dict = None):
                self.page_content = page_content
                self.metadata = metadata or {}


class TestChunking(unittest.TestCase):
    """Verify text splitting produces multiple chunks with preserved metadata."""

    def setUp(self):
        self.splitter = MathTextSplitter(chunk_size=200, chunk_overlap=20)

    def test_splits_large_doc(self):
        """A large document should be split into more than one chunk."""
        doc = Document(
            page_content="Math paragraph with content. " * 60,
            metadata={"source": "test"},
        )
        self.assertGreater(len(self.splitter.split_document(doc)), 1)

    def test_metadata_preserved(self):
        """All chunks must carry the original document's metadata plus chunk_index."""
        doc = Document(
            page_content="x " * 500,
            metadata={"source": "test.pdf", "topic": "algebra"},
        )
        for chunk in self.splitter.split_document(doc):
            self.assertEqual(chunk.metadata.get("topic"), "algebra")
            self.assertIn("chunk_index", chunk.metadata)


if __name__ == "__main__":
    unittest.main()
