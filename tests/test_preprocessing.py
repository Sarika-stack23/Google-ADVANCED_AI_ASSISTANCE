"""Tests for MathDataPreprocessor — extracted from main.py L2596-L2618.

Validates text cleaning, deduplication by MD5 hash, topic detection,
and rejection of documents that are too short.
"""

import unittest
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import MathDataPreprocessor

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


class TestPreprocessing(unittest.TestCase):
    """Verify preprocessing: whitespace cleanup, dedup, topic detection, min-length."""

    def setUp(self):
        self.pp = MathDataPreprocessor()

    def test_cleans_whitespace(self):
        """Multi-line whitespace should be collapsed."""
        doc = Document(
            page_content="Hello   World   Math   content   here   is   important   for   the   derivative   test",
            metadata={},
        )
        result = self.pp.preprocess_document(doc)
        self.assertIsNotNone(result)
        self.assertNotIn("   ", result.page_content)

    def test_deduplication(self):
        """Identical documents (by MD5 hash) should be rejected on second pass."""
        doc = Document(
            page_content="The derivative of x squared is 2x. " * 10,
            metadata={},
        )
        self.assertIsNotNone(self.pp.preprocess_document(doc))
        self.assertIsNone(self.pp.preprocess_document(doc))

    def test_topic_detection(self):
        """Calculus keywords should be detected as 'calculus' topic."""
        doc = Document(
            page_content="The derivative and integral of functions in calculus.",
            metadata={},
        )
        result = self.pp.preprocess_document(doc)
        self.assertEqual(result.metadata["topic"], "calculus")

    def test_skips_short(self):
        """Documents shorter than minimum length should be rejected."""
        self.assertIsNone(
            MathDataPreprocessor().preprocess_document(
                Document(page_content="too short", metadata={})
            )
        )


if __name__ == "__main__":
    unittest.main()
