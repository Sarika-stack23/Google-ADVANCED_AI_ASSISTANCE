"""Tests for Gemini Service — Phase 2 Verification.

Validates:
- Gemini text query processing
- Gemini Vision math extraction
- Automatic fallback from primary to fallback model
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import asyncio

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.src.config import settings
from backend.src.services.gemini_service import GeminiService, GeminiVisionService


class TestGeminiService(unittest.TestCase):
    """Verify Gemini text query logic."""

    @patch("backend.src.services.gemini_service._get_gemini_client")
    def test_query_success(self, mock_get_client):
        """Test a successful query to Gemini."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "This is a test response."
        mock_client.models.generate_content.return_value = mock_response

        service = GeminiService()
        response = service.query("test question")

        self.assertEqual(response, "This is a test response.")
        mock_client.models.generate_content.assert_called_once()

    @patch("backend.src.services.gemini_service._get_gemini_client")
    def test_query_fallback(self, mock_get_client):
        """Test fallback when the primary model fails (e.g. rate limit)."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # We need the first model to raise an Exception, and the second to succeed
        def side_effect(*args, **kwargs):
            if kwargs.get('model') == "gemini-2.0-flash":
                raise Exception("429 Resource Exhausted")
            mock_resp = MagicMock()
            mock_resp.text = "Fallback response"
            return mock_resp
            
        mock_client.models.generate_content.side_effect = side_effect

        service = GeminiService()
        response = service.query("test question")

        self.assertIn("Fallback response", response)
        self.assertIn("gemini-1.5-flash", response)


class TestGeminiVisionService(unittest.TestCase):

    @patch("backend.src.services.gemini_service._get_gemini_client")
    def test_extract_math(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "x^2 + y^2 = r^2"
        mock_client.models.generate_content.return_value = mock_response

        service = GeminiVisionService()
        result = service.extract_math_from_image(b"fakebytes", "image/png")

        self.assertEqual(result, "x^2 + y^2 = r^2")

    @patch("backend.src.services.gemini_service._get_gemini_client")
    def test_extract_and_solve(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "EXTRACTED: 2+2\n---\nSOLUTION: It is 4."
        mock_client.models.generate_content.return_value = mock_response

        service = GeminiVisionService()
        result = service.extract_and_solve(b"fakebytes", "image/png")

        self.assertEqual(result["extracted"], "2+2")
        self.assertEqual(result["solution"], "It is 4.")


if __name__ == "__main__":
    unittest.main()
