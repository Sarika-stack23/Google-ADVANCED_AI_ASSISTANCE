"""Tests for Firebase Auth Middleware and Progress API — Phase 3 Verification."""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.src.api.v1.progress import router as progress_router
from backend.src.api.middleware.auth import verify_firebase_token
from backend.src.config import settings

# Create a test app
app = FastAPI()
app.include_router(progress_router)

client = TestClient(app)

class TestFirebaseAuth(unittest.TestCase):
    """Verify Firebase middleware functionality."""

    @patch("backend.src.api.middleware.auth.get_auth")
    def test_verify_valid_token(self, mock_get_auth):
        """Test with a valid token."""
        mock_auth = MagicMock()
        mock_decoded = {"uid": "valid-user-123"}
        mock_auth.verify_id_token.return_value = mock_decoded
        mock_get_auth.return_value = mock_auth

        # Enable Firebase for test
        old_use_firebase = settings.use_firebase
        settings.use_firebase = True

        from fastapi.security import HTTPAuthorizationCredentials
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="real-token")
        
        try:
            uid = verify_firebase_token(creds)
            self.assertEqual(uid, "valid-user-123")
        finally:
            settings.use_firebase = old_use_firebase

    @patch("backend.src.api.middleware.auth.get_auth")
    def test_verify_missing_token(self, mock_get_auth):
        """Test with no token."""
        mock_get_auth.return_value = MagicMock()
        old_use_firebase = settings.use_firebase
        settings.use_firebase = True
        
        from fastapi import HTTPException
        
        try:
            with self.assertRaises(HTTPException) as context:
                verify_firebase_token(None)
            self.assertEqual(context.exception.status_code, 401)
        finally:
            settings.use_firebase = old_use_firebase

    def test_firebase_disabled_fallback(self):
        """Test that missing Firebase falls back to anonymous if disabled."""
        old_use_firebase = settings.use_firebase
        settings.use_firebase = False
        
        try:
            uid = verify_firebase_token(None)
            self.assertEqual(uid, "anonymous")
        finally:
            settings.use_firebase = old_use_firebase

class TestProgressAPI(unittest.TestCase):
    """Verify /api/v1/progress endpoints."""

    @patch("backend.src.api.v1.progress.get_firestore_client")
    def test_get_progress_empty(self, mock_get_client):
        """Test fetching progress for a new user."""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = False
        
        mock_db.collection().document().collection().document().get.return_value = mock_doc
        mock_get_client.return_value = mock_db
        
        # We can bypass middleware by sending test-token (which returns test-user-uid)
        response = client.get("/api/v1/progress", headers={"Authorization": "Bearer test-token"})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["streak"], 0)
        self.assertEqual(data["total_solved"], 0)

if __name__ == "__main__":
    unittest.main()
