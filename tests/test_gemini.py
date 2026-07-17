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

    @patch("backend.src.services.gemini_service._get_gemini_model")
    def test_query_success(self, mock_get_model):
        """Test a successful text query."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Here is the solution."
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model

        service = GeminiService()
        result = service.query("solve x + 2 = 5")
        
        self.assertEqual(result, "Here is the solution.")
        mock_get_model.assert_called_with(settings.gemini_primary_model)

    @patch("backend.src.services.gemini_service._get_gemini_model")
    def test_query_fallback(self, mock_get_model):
        """Test fallback to secondary model on rate limit."""
        mock_primary = MagicMock()
        mock_primary.generate_content.side_effect = Exception("429 Resource Exhausted")
        
        mock_fallback = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Fallback solution."
        mock_fallback.generate_content.return_value = mock_response
        
        # Return primary on first call, fallback on second
        mock_get_model.side_effect = [mock_primary, mock_fallback]

        service = GeminiService()
        result = service.query("solve x + 2 = 5")
        
        self.assertIn("Fallback solution.", result)
        self.assertIn("Using fallback", result)
        self.assertEqual(mock_get_model.call_count, 2)


class TestGeminiVisionService(unittest.TestCase):
    """Verify Gemini Vision math extraction."""

    @patch("backend.src.services.gemini_service._get_gemini_model")
    def test_extract_math(self, mock_get_model):
        """Test vision extraction."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "x^2 + y^2 = r^2"
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model

        service = GeminiVisionService()
        result = service.extract_math_from_image(b"fake_image_data")
        
        self.assertEqual(result, "x^2 + y^2 = r^2")
        mock_get_model.assert_called_with(settings.gemini_vision_model)

    @patch("backend.src.services.gemini_service._get_gemini_model")
    def test_extract_and_solve(self, mock_get_model):
        """Test combined extraction and solving."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "EXTRACTED: x + 2 = 5\n---\nSOLUTION:\nSubtract 2: x = 3"
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model

        service = GeminiVisionService()
        result = service.extract_and_solve(b"fake_image_data")
        
        self.assertEqual(result["extracted"], "x + 2 = 5")
        self.assertEqual(result["solution"], "Subtract 2: x = 3")


if __name__ == "__main__":
    unittest.main()
