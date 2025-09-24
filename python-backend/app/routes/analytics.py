"""
Analytics routes for Python backend
"""

from fastapi import APIRouter, Depends
from app.routes.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/performance")
async def get_user_performance(current_user: User = Depends(get_current_user)):
    """Get user performance analytics"""
    return {
        "message": "Analytics endpoint - Python backend",
        "user_id": str(current_user.id),
        "performance_metrics": current_user.performance_metrics.dict()
    }
