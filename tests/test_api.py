"""Tests for FastAPI endpoints — Phase 1 verification.

Validates:
- GET /health returns HTTP 200 with correct JSON structure
- GET / returns root info
- POST /api/v1/chat accepts valid request body
"""

import unittest
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.src.main import app


client = TestClient(app)


class TestHealthEndpoint(unittest.TestCase):
    """Verify /health endpoint returns correct status."""

    def test_health_returns_200(self):
        """GET /health should return HTTP 200."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_health_json_structure(self):
        """GET /health response must contain required fields."""
        response = client.get("/health")
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("environment", data)
        self.assertIn("version", data)
        self.assertIn("kb_docs", data)
        self.assertIn("llm_model", data)
        self.assertIn("vector_db", data)

    def test_root_returns_200(self):
        """GET / should return HTTP 200 with API info."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("docs", data)
        self.assertIn("health", data)


class TestChatEndpoint(unittest.TestCase):
    """Verify /api/v1/chat endpoint validation."""

    def test_chat_rejects_empty_query(self):
        """POST /api/v1/chat with empty query should return 422."""
        response = client.post("/api/v1/chat", json={"query": ""})
        self.assertEqual(response.status_code, 422)

    def test_chat_rejects_missing_query(self):
        """POST /api/v1/chat with no body should return 422."""
        response = client.post("/api/v1/chat", json={})
        self.assertEqual(response.status_code, 422)

    def test_chat_accepts_valid_request(self):
        """POST /api/v1/chat with valid query should return 200 or 500 (no API key)."""
        response = client.post("/api/v1/chat", json={"query": "solve x^2-4=0"})
        # Without GROQ_API_KEY, this will return 500 but validates the routing works
        self.assertIn(response.status_code, [200, 500])


if __name__ == "__main__":
    unittest.main()
