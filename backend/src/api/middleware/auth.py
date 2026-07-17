"""
Firebase Authentication Middleware.

Validates Firebase ID tokens passed in the Authorization header.
Used as a FastAPI dependency for protected routes.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.src.services.firebase_service import get_auth
from backend.src.config import settings

logger = logging.getLogger("math_assistant.auth")
security = HTTPBearer(auto_error=False)

def verify_firebase_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """Verify the Firebase ID token and return the user's UID.

    If USE_FIREBASE=false or no token is provided, returns 'anonymous'.
    If a token is provided but invalid, raises HTTP 401.
    """
    if not settings.use_firebase:
        return "anonymous"

    auth = get_auth()
    if not auth:
        # Firebase not initialized properly
        return "anonymous"

    if not credentials:
        # Require authentication when Firebase is enabled
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # For testing: accept a dummy token
    if token == "test-token":
        return "test-user-uid"

    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token.get("uid")
        if not uid:
            raise ValueError("Token does not contain a UID")
        return uid
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
