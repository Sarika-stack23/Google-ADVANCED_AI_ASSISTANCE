"""Tests for the PromptService."""

import unittest
from unittest.mock import patch, MagicMock
from backend.src.services.prompt_service import PromptService, DEFAULT_SYSTEM_PROMPT

class TestPromptService(unittest.TestCase):

    @patch("backend.src.services.prompt_service.firestore")
    def test_fallback_when_firestore_disabled(self, mock_firestore):
        """Should return the local default prompt when firestore is disabled."""
        with patch("backend.src.services.prompt_service.settings.use_firebase", False):
            service = PromptService()
            prompt = service.get_system_prompt()
        
        self.assertEqual(prompt, DEFAULT_SYSTEM_PROMPT)
        mock_firestore.Client.assert_not_called()

    @patch("backend.src.services.prompt_service.firestore")
    def test_fallback_when_doc_missing(self, mock_firestore):
        """Should return the local default prompt when Firestore doc doesn't exist."""
        # Setup mock db
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection().document().get.return_value = mock_doc
        
        with patch("backend.src.services.prompt_service.settings.use_firebase", True):
            service = PromptService()
            service.db = mock_db
            prompt = service.get_system_prompt()
            
        self.assertEqual(prompt, DEFAULT_SYSTEM_PROMPT)

    @patch("backend.src.services.prompt_service.firestore")
    def test_fetches_versioned_prompt(self, mock_firestore):
        """Should return the requested version from Firestore."""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "active_version": "v1",
            "versions": {
                "v1": "Hello v1",
                "v2": "Hello v2"
            }
        }
        mock_db.collection().document().get.return_value = mock_doc
        
        with patch("backend.src.services.prompt_service.settings.use_firebase", True):
            service = PromptService()
            service.db = mock_db
            
            # Fetch latest (should resolve to active_version v1)
            prompt_latest = service.get_system_prompt(version="latest")
            self.assertEqual(prompt_latest, "Hello v1")
            
            # Fetch v2 explicitly
            prompt_v2 = service.get_system_prompt(version="v2")
            self.assertEqual(prompt_v2, "Hello v2")

if __name__ == "__main__":
    unittest.main()
