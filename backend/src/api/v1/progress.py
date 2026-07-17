"""
Progress Tracking API — /api/v1/progress endpoints.

Handles daily streak calculations and total problems solved per user.
Backed by Firestore.
"""

import logging
from datetime import datetime, timezone
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException

from backend.src.api.middleware.auth import verify_firebase_token
from backend.src.services.firebase_service import get_firestore_client

logger = logging.getLogger("math_assistant.api.progress")

router = APIRouter(prefix="/api/v1/progress", tags=["progress"])

class ProgressResponse(BaseModel):
    streak: int
    total_solved: int
    last_solved_date: str

@router.get("", response_model=ProgressResponse)
async def get_progress(uid: str = Depends(verify_firebase_token)):
    """Get the user's current progress and streak."""
    db = get_firestore_client()
    if not db:
        # Fallback if Firebase is disabled
        return ProgressResponse(streak=0, total_solved=0, last_solved_date="")
        
    try:
        doc_ref = db.collection("users").document(uid).collection("profile").document("stats")
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            return ProgressResponse(
                streak=data.get("streak", 0),
                total_solved=data.get("total_solved", 0),
                last_solved_date=data.get("last_solved_date", "")
            )
        else:
            return ProgressResponse(streak=0, total_solved=0, last_solved_date="")
    except Exception as e:
        logger.error(f"Error getting progress for {uid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/increment", response_model=ProgressResponse)
async def increment_progress(uid: str = Depends(verify_firebase_token)):
    """Increment the user's total solved count and update their streak."""
    db = get_firestore_client()
    if not db:
        return ProgressResponse(streak=1, total_solved=1, last_solved_date=datetime.now(timezone.utc).date().isoformat())

    try:
        doc_ref = db.collection("users").document(uid).collection("profile").document("stats")
        today_str = datetime.now(timezone.utc).date().isoformat()
        
        # We need a transaction to safely update the streak
        @from_firestore_transaction(db)
        def update_in_transaction(transaction, ref, today):
            snapshot = ref.get(transaction=transaction)
            
            if not snapshot.exists:
                data = {
                    "streak": 1,
                    "total_solved": 1,
                    "last_solved_date": today
                }
                transaction.set(ref, data)
                return data
                
            current_data = snapshot.to_dict()
            last_date = current_data.get("last_solved_date", "")
            streak = current_data.get("streak", 0)
            total = current_data.get("total_solved", 0) + 1
            
            if last_date == today:
                # Already solved a problem today, just increment total
                pass
            else:
                # Need to check if it was yesterday
                try:
                    last_date_obj = datetime.fromisoformat(last_date).date()
                    today_obj = datetime.fromisoformat(today).date()
                    delta = (today_obj - last_date_obj).days
                    
                    if delta == 1:
                        streak += 1
                    else:
                        streak = 1
                except ValueError:
                    streak = 1
                    
            data = {
                "streak": streak,
                "total_solved": total,
                "last_solved_date": today
            }
            transaction.update(ref, data)
            return data
            
        new_stats = update_in_transaction(db.transaction(), doc_ref, today_str)
        return ProgressResponse(**new_stats)
        
    except Exception as e:
        logger.error(f"Error incrementing progress for {uid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def from_firestore_transaction(db):
    """Helper decorator for Firestore transactions."""
    from firebase_admin import firestore
    return firestore.transactional
