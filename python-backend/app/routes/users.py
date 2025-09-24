"""
User routes for Python backend
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.routes.auth import get_current_user
from app.models.user import User
from typing import Optional

router = APIRouter()

@router.get("/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get user profile"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "firstName": current_user.first_name,  # Use camelCase for frontend
        "lastName": current_user.last_name,    # Use camelCase for frontend
        "role": current_user.role,
        "institution": current_user.institution,
        "department": current_user.department,
        "year": current_user.year,
        "rollNumber": current_user.roll_number,  # Use camelCase for frontend
        "is_active": current_user.is_active,
        "last_login": current_user.last_login,
        "student_profile": current_user.student_profile.dict() if current_user.student_profile else None,
        "performance_metrics": current_user.performance_metrics.dict()
    }

@router.get("/{user_id}/analytics")
async def get_user_analytics(
    user_id: str,
    period: Optional[str] = "30d",
    current_user: User = Depends(get_current_user)
):
    """Get user analytics by user ID"""
    # Check if user is accessing their own analytics or is admin/instructor
    if str(current_user.id) != user_id and current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get the target user
    target_user = await User.get(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": str(target_user.id),
        "period": period,
        "performance_metrics": target_user.performance_metrics.dict(),
        "student_profile": target_user.student_profile.dict() if target_user.student_profile else None,
        "analytics": {
            "total_assessments": target_user.performance_metrics.total_assessments,
            "average_score": target_user.performance_metrics.average_score,
            "improvement_rate": target_user.performance_metrics.improvement_rate,
            "strengths": target_user.performance_metrics.strengths,
            "weaknesses": target_user.performance_metrics.weaknesses,
            "recommended_topics": target_user.performance_metrics.recommended_topics
        }
    }
