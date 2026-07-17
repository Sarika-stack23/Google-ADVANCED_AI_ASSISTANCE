"""Tests for MathDataLoader — extracted from main.py L2589-L2594.

Validates that the built-in NCERT knowledge base loads correctly
with non-empty content and proper metadata tagging.
"""

import unittest
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import MathDataLoader


class TestDataSources(unittest.TestCase):
    """Verify NCERT knowledge base loading produces valid Document objects."""

    def test_builtin_knowledge(self):
        """Knowledge base must return non-empty documents with topic metadata."""
        docs = MathDataLoader().load_builtin_knowledge()
        self.assertGreater(len(docs), 0)
        self.assertTrue(all(len(d.page_content) > 50 for d in docs))
        self.assertTrue(all("topic" in d.metadata for d in docs))


if __name__ == "__main__":
    unittest.main()
