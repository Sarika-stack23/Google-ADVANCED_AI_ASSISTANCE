"""
Progress Tracking API — /api/v1/progress endpoints.

Handles daily streak calculations and total problems solved per user.
Backed by Firestore.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List
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
    activity_map: Dict[str, int] = {}
    weak_topics: List[str] = []
    accuracy: int = 100

_MEMORY_STORE: Dict[str, dict] = {}

def get_memory_stats(uid: str) -> dict:
    if uid not in _MEMORY_STORE:
        _MEMORY_STORE[uid] = {
            "streak": 0,
            "total_solved": 0,
            "last_solved_date": "",
            "activity_map": {},
            "weak_topics": [],
            "accuracy": 100,
            "correct_answers": 0,
            "total_answers": 0
        }
    return _MEMORY_STORE[uid]

@router.get("", response_model=ProgressResponse)
async def get_progress(uid: str = Depends(verify_firebase_token)):
    """Get the user's current progress and streak."""
    db = get_firestore_client()
    if not db:
        # Fallback if Firebase is disabled
        stats = get_memory_stats(uid)
        return ProgressResponse(**{k: v for k, v in stats.items() if k in ProgressResponse.__fields__})
        
    try:
        doc_ref = db.collection("users").document(uid).collection("profile").document("stats")
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            return ProgressResponse(
                streak=data.get("streak", 0),
                total_solved=data.get("total_solved", 0),
                last_solved_date=data.get("last_solved_date", ""),
                activity_map=data.get("activity_map", {}),
                weak_topics=data.get("weak_topics", []),
                accuracy=data.get("accuracy", 100)
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
    today_str = datetime.now(timezone.utc).date().isoformat()
    if not db:
        stats = get_memory_stats(uid)
        last_date = stats.get("last_solved_date", "")
        streak = stats.get("streak", 0)
        total = stats.get("total_solved", 0) + 1
        activity_map = stats.get("activity_map", {})
        activity_map[today_str] = activity_map.get(today_str, 0) + 1
        
        if last_date != today_str:
            try:
                if last_date:
                    delta = (datetime.fromisoformat(today_str).date() - datetime.fromisoformat(last_date).date()).days
                    streak = (streak + 1) if delta == 1 else 1
                else:
                    streak = 1
            except ValueError:
                streak = 1
                
        stats.update({
            "streak": streak,
            "total_solved": total,
            "last_solved_date": today_str,
            "activity_map": activity_map
        })
        return ProgressResponse(**{k: v for k, v in stats.items() if k in ProgressResponse.__fields__})
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
                    "last_solved_date": today,
                    "activity_map": {today: 1},
                    "weak_topics": [],
                    "accuracy": 100,
                    "correct_answers": 1,
                    "total_answers": 1
                }
                transaction.set(ref, data)
                return data
                
            current_data = snapshot.to_dict()
            last_date = current_data.get("last_solved_date", "")
            streak = current_data.get("streak", 0)
            total = current_data.get("total_solved", 0) + 1
            activity_map = current_data.get("activity_map", {})
            
            activity_map[today] = activity_map.get(today, 0) + 1
            
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
                "last_solved_date": today,
                "activity_map": activity_map,
                "weak_topics": current_data.get("weak_topics", []),
                "accuracy": current_data.get("accuracy", 100)
            }
            transaction.update(ref, data)
            return data
            
        new_stats = update_in_transaction(db.transaction(), doc_ref, today_str)
        return ProgressResponse(**new_stats)
        
    except Exception as e:
        logger.error(f"Error incrementing progress for {uid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class WeaknessRequest(BaseModel):
    topic: str

@router.post("/weakness", response_model=ProgressResponse)
async def add_weakness(req: WeaknessRequest, uid: str = Depends(verify_firebase_token)):
    """Add a topic to the user's weak topics list."""
    db = get_firestore_client()
    if not db:
        stats = get_memory_stats(uid)
        topics = stats.get("weak_topics", [])
        if req.topic not in topics:
            topics.append(req.topic)
            if len(topics) > 5:
                topics = topics[-5:]
        stats["weak_topics"] = topics
        return ProgressResponse(**{k: v for k, v in stats.items() if k in ProgressResponse.__fields__})
        
    doc_ref = db.collection("users").document(uid).collection("profile").document("stats")
    
    @from_firestore_transaction(db)
    def update_weakness(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists:
            data = {"streak": 0, "total_solved": 0, "last_solved_date": "", "weak_topics": [req.topic], "accuracy": 100}
            transaction.set(ref, data)
            return data
            
        data = snapshot.to_dict()
        topics = data.get("weak_topics", [])
        if req.topic not in topics:
            topics.append(req.topic)
            # keep only last 5
            if len(topics) > 5:
                topics = topics[-5:]
        
        update_data = {"weak_topics": topics}
        transaction.update(ref, update_data)
        data.update(update_data)
        return data
        
    try:
        new_stats = update_weakness(db.transaction(), doc_ref)
        return ProgressResponse(
            streak=new_stats.get("streak", 0),
            total_solved=new_stats.get("total_solved", 0),
            last_solved_date=new_stats.get("last_solved_date", ""),
            activity_map=new_stats.get("activity_map", {}),
            weak_topics=new_stats.get("weak_topics", []),
            accuracy=new_stats.get("accuracy", 100)
        )
    except Exception as e:
        logger.error(f"Error updating weakness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class AccuracyRequest(BaseModel):
    correct: bool

@router.post("/accuracy", response_model=ProgressResponse)
async def update_accuracy(req: AccuracyRequest, uid: str = Depends(verify_firebase_token)):
    """Update user's accuracy based on a correct/incorrect answer."""
    db = get_firestore_client()
    if not db:
        stats = get_memory_stats(uid)
        correct_ans = stats.get("correct_answers", 0) + (1 if req.correct else 0)
        total_ans = stats.get("total_answers", 0) + 1
        acc = int((correct_ans / total_ans) * 100)
        stats.update({
            "correct_answers": correct_ans,
            "total_answers": total_ans,
            "accuracy": acc
        })
        return ProgressResponse(**{k: v for k, v in stats.items() if k in ProgressResponse.__fields__})
        
    doc_ref = db.collection("users").document(uid).collection("profile").document("stats")
    
    @from_firestore_transaction(db)
    def update_acc(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists:
            data = {
                "streak": 0, "total_solved": 0, "last_solved_date": "",
                "correct_answers": 1 if req.correct else 0,
                "total_answers": 1,
                "accuracy": 100 if req.correct else 0
            }
            transaction.set(ref, data)
            return data
            
        data = snapshot.to_dict()
        correct_ans = data.get("correct_answers", 0) + (1 if req.correct else 0)
        total_ans = data.get("total_answers", 0) + 1
        acc = int((correct_ans / total_ans) * 100)
        
        update_data = {
            "correct_answers": correct_ans,
            "total_answers": total_ans,
            "accuracy": acc
        }
        transaction.update(ref, update_data)
        data.update(update_data)
        return data
        
    try:
        new_stats = update_acc(db.transaction(), doc_ref)
        return ProgressResponse(
            streak=new_stats.get("streak", 0),
            total_solved=new_stats.get("total_solved", 0),
            last_solved_date=new_stats.get("last_solved_date", ""),
            activity_map=new_stats.get("activity_map", {}),
            weak_topics=new_stats.get("weak_topics", []),
            accuracy=new_stats.get("accuracy", 100)
        )
    except Exception as e:
        logger.error(f"Error updating accuracy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def from_firestore_transaction(db):
    """Helper decorator for Firestore transactions."""
    from firebase_admin import firestore
    return firestore.transactional
