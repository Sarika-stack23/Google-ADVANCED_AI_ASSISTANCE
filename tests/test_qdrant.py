"""Tests for Phase 6 Qdrant integration."""

import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from backend.src.services.qdrant_service import QdrantService
from backend.src.math.knowledge_indexer import KnowledgeIndexer

class TestQdrantService(unittest.TestCase):

    @patch("backend.src.services.qdrant_service.get_dense_embeddings")
    @patch("backend.src.services.qdrant_service.QdrantClient")
    @patch("backend.src.services.qdrant_service.FastEmbedSparse")
    @patch("backend.src.services.qdrant_service.QdrantVectorStore")
    def test_qdrant_initialization_memory(
        self, mock_qdrant_vs, mock_fastembed, mock_client, mock_get_dense
    ):
        """Test Qdrant initializes in memory mode successfully."""
        service = QdrantService()
        mock_client.assert_called_with(location=":memory:")
        mock_get_dense.assert_called_once()
        mock_fastembed.assert_called_once()
        mock_qdrant_vs.assert_called_once()

    @patch("backend.src.services.qdrant_service.QdrantVectorStore")
    def test_qdrant_similarity_search(self, mock_qdrant_vs):
        """Test Qdrant passes filter conditions."""
        mock_vs_instance = MagicMock()
        mock_qdrant_vs.return_value = mock_vs_instance
        
        service = QdrantService()
        
        service.similarity_search(
            query="test",
            filter_class="class_10",
            filter_chapter="ch6"
        )
        
        mock_vs_instance.similarity_search.assert_called_once()
        kwargs = mock_vs_instance.similarity_search.call_args.kwargs
        self.assertEqual(kwargs['query'], "test")
        self.assertIsNotNone(kwargs['filter'])


class TestKnowledgeIndexer(unittest.TestCase):

    def test_parse_frontmatter(self):
        indexer = KnowledgeIndexer()
        
        test_md = "---\ntopic: geometry\nclass_level: class_10\n---\n\nContent goes here."
        metadata, content = indexer.parse_frontmatter(test_md)
        
        self.assertEqual(metadata["topic"], "geometry")
        self.assertEqual(metadata["class_level"], "class_10")
        self.assertEqual(content, "Content goes here.")

if __name__ == "__main__":
    unittest.main()
