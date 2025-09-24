"""
Admin routes for Python backend
Equivalent to Node.js admin routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any
from datetime import datetime, timedelta
from app.routes.auth import get_current_user
from app.models.user import User, UserRole
from app.models.assessment import Assessment, AssessmentStatus
from app.models.question import Question

router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/dashboard")
async def get_admin_dashboard(admin_user: User = Depends(require_admin)):
    """Get system overview dashboard"""
    try:
        now = datetime.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)

        # User statistics
        total_users = await User.count()
        active_users = await User.find(User.is_active == True).count()
        new_users_30_days = await User.find(User.created_at >= last_30_days).count()
        new_users_7_days = await User.find(User.created_at >= last_7_days).count()

        # Users by role
        users_by_role = {}
        for role in UserRole:
            count = await User.find(User.role == role).count()
            users_by_role[role.value] = count

        # Assessment statistics
        total_assessments = await Assessment.count()
        completed_assessments = await Assessment.find(Assessment.status == AssessmentStatus.COMPLETED).count()
        assessments_30_days = await Assessment.find(Assessment.created_at >= last_30_days).count()

        # Question statistics
        total_questions = await Question.count()
        active_questions = await Question.find(Question.is_active == True).count()

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "new_30_days": new_users_30_days,
                "new_7_days": new_users_7_days,
                "by_role": users_by_role
            },
            "assessments": {
                "total": total_assessments,
                "completed": completed_assessments,
                "last_30_days": assessments_30_days
            },
            "questions": {
                "total": total_questions,
                "active": active_questions
            },
            "system": {
                "status": "healthy",
                "last_updated": now.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching admin dashboard: {str(e)}"
        )

@router.get("/users")
async def get_all_users(
    page: int = 1,
    limit: int = 20,
    role: str = None,
    admin_user: User = Depends(require_admin)
):
    """Get all users with pagination"""
    try:
        query = {}
        if role:
            query["role"] = role

        skip = (page - 1) * limit
        users = await User.find(query).skip(skip).limit(limit).to_list()
        
        total = await User.find(query).count()

        return {
            "users": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "institution": user.institution,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "last_login": user.last_login
                }
                for user in users
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    admin_user: User = Depends(require_admin)
):
    """Update user active status"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_active = is_active
        await user.save()

        return {
            "message": f"User {'activated' if is_active else 'deactivated'} successfully",
            "user_id": user_id,
            "is_active": is_active
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user status: {str(e)}"
        )

@router.get("/assessments")
async def get_all_assessments(
    page: int = 1,
    limit: int = 20,
    status: str = None,
    admin_user: User = Depends(require_admin)
):
    """Get all assessments with pagination"""
    try:
        query = {}
        if status:
            query["status"] = status

        skip = (page - 1) * limit
        assessments = await Assessment.find(query).skip(skip).limit(limit).to_list()
        
        total = await Assessment.find(query).count()

        return {
            "assessments": [
                {
                    "id": str(assessment.id),
                    "user_id": assessment.user_id,
                    "title": assessment.title,
                    "assessment_type": assessment.assessment_type,
                    "subject": assessment.subject,
                    "status": assessment.status,
                    "created_at": assessment.created_at,
                    "completed_at": assessment.end_time,
                    "score": assessment.results.score if assessment.results else None
                }
                for assessment in assessments
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching assessments: {str(e)}"
        )

@router.get("/questions")
async def get_all_questions(
    page: int = 1,
    limit: int = 20,
    subject: str = None,
    difficulty: str = None,
    admin_user: User = Depends(require_admin)
):
    """Get all questions with pagination"""
    try:
        query = {}
        if subject:
            query["subject"] = subject
        if difficulty:
            query["difficulty"] = difficulty

        skip = (page - 1) * limit
        questions = await Question.find(query).skip(skip).limit(limit).to_list()
        
        total = await Question.find(query).count()

        return {
            "questions": [
                {
                    "id": str(question.id),
                    "question_text": question.question_text,
                    "subject": question.subject,
                    "topic": question.topic,
                    "difficulty": question.difficulty,
                    "difficulty_score": question.difficulty_score,
                    "is_active": question.is_active,
                    "created_at": question.created_at,
                    "usage_stats": question.usage_stats.dict() if question.usage_stats else None
                }
                for question in questions
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching questions: {str(e)}"
        )
