"""Tests for EvaluationService."""

import unittest
from unittest.mock import patch, MagicMock
from backend.src.services.evaluation_service import EvaluationService

class TestEvaluationService(unittest.TestCase):

    @patch("google.genai.Client")
    def test_evaluate_answer_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "SCORE: 4\nREASONING: The steps are correct but the final simplification could be better."
        mock_client.models.generate_content.return_value = mock_response
        
        with patch("backend.src.services.evaluation_service.settings.gemini_api_key", "fake-key"):
            service = EvaluationService()
            result = service.evaluate_answer("2+2", "4", "4")
            
        self.assertEqual(result["score"], 4)
        self.assertIn("simplification", result["reasoning"])

    @patch("backend.src.services.evaluation_service.EvaluationService.evaluate_answer")
    def test_run_eval_pipeline(self, mock_eval):
        mock_eval.side_effect = [
            {"score": 5, "reasoning": "Perfect."},
            {"score": 3, "reasoning": "Okay."}
        ]
        
        test_cases = [
            {"question": "Q1", "generated_answer": "A1", "reference_answer": "R1"},
            {"question": "Q2", "generated_answer": "A2", "reference_answer": "R2"}
        ]
        
        service = EvaluationService()
        result = service.run_eval_pipeline(test_cases)
        
        self.assertEqual(result["average_score"], 4.0)
        self.assertEqual(result["total_evaluated"], 2)
        self.assertEqual(len(result["results"]), 2)

if __name__ == "__main__":
    unittest.main()
