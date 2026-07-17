import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.api.middleware.auth import verify_firebase_token
from unittest.mock import patch, MagicMock

# Mock auth dependency
async def override_verify_token():
    return "test-uid-123"

app.dependency_overrides[verify_firebase_token] = override_verify_token

client = TestClient(app)

@patch("backend.src.api.v1.chat.math_graph.invoke")
@patch("backend.src.config.settings.use_langgraph", True)
def test_rate_limiter_blocks_excessive_requests(mock_invoke):
    """Verify that slowapi limits requests to 20/minute."""
    
    mock_invoke.return_value = {"final_answer": "Mocked answer"}
    
    payload = {
        "query": "2+2",
        "session_id": "test_session"
    }
    
    # Send 30 requests
    for _ in range(30):
        response = client.post("/api/v1/chat", json={"query": "test", "session_id": "test"})
    
    # The request should be rate limited
    response_429 = client.post("/api/v1/chat", json=payload)
    assert response_429.status_code == 429
    assert "Rate limit exceeded" in response_429.text
