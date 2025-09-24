"""
Question routes for Python backend
"""

from fastapi import APIRouter, Depends
from app.routes.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_questions(current_user: User = Depends(get_current_user)):
    """Get questions"""
    return {
        "message": "Questions endpoint - Python backend",
        "user_id": str(current_user.id)
    }
