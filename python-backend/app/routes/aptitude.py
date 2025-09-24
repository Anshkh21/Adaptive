"""
Aptitude test routes for Python backend
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.aptitude_test import AptitudeTest
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AptitudeTestResponse(BaseModel):
    id: str
    title: str
    description: str
    test_type: str
    duration_minutes: int
    total_questions: int
    passing_score: float
    is_available: bool

@router.get("")
@router.get("/")
async def get_aptitude_tests(current_user: User = Depends(get_current_user)):
    """Get available aptitude tests"""
    try:
        print(f"Getting aptitude tests for user: {current_user.id}")
        
        # Get all available aptitude tests
        tests = await AptitudeTest.find(AptitudeTest.is_active == True).to_list()
        
        print(f"Found {len(tests)} aptitude tests")
        
        test_list = []
        for test in tests:
            print(f"Processing test: {test.title}")
            test_data = {
                "_id": str(test.id),  # Frontend expects _id
                "title": test.title,
                "description": test.description,
                "type": test.type,  # Frontend expects type, not test_type
                "config": {
                    "totalQuestions": len(test.questions),  # Frontend expects config.totalQuestions
                    "timeLimit": test.config.time_limit,  # Frontend expects config.timeLimit in seconds
                    "passingScore": test.config.passing_score,
                    "maxAttempts": test.config.max_attempts
                },
                "usageStats": {
                    "totalAttempts": test.usage_stats.total_attempts,
                    "averageScore": test.usage_stats.average_score,
                    "completionRate": test.usage_stats.completion_rate
                }
            }
            test_list.append(test_data)
        
        print(f"Returning {len(test_list)} tests")
        
        return test_list  # Return the array directly, not wrapped in an object
    except Exception as e:
        print(f"Error fetching aptitude tests: {e}")
        return []  # Return empty array on error

@router.get("/history")
async def get_aptitude_history(
    current_user: User = Depends(get_current_user)
):
    """Get user's aptitude test history"""
    try:
        if not current_user.aptitude_history:
            return []
        
        # Return history sorted by completion date (newest first)
        history = sorted(
            current_user.aptitude_history,
            key=lambda x: x.completed_at,
            reverse=True
        )
        
        # Convert to frontend-friendly format
        history_data = []
        for entry in history:
            history_data.append({
                "testId": entry.test_id,
                "testTitle": entry.test_title,
                "testType": entry.test_type,
                "score": entry.score,
                "passed": entry.passed,
                "completedAt": entry.completed_at.isoformat(),
                "timeSpent": entry.time_spent,
                "totalQuestions": len(entry.answers),
                "correctAnswers": len([a for a in entry.answers if a.answer == 0])  # Mock: assume answer 0 is correct
            })
        
        return history_data
        
    except Exception as e:
        print(f"Error fetching aptitude history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch aptitude history: {str(e)}"
        )

@router.get("/{test_id}")
async def get_aptitude_test(
    test_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific aptitude test"""
    try:
        test = await AptitudeTest.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aptitude test not found"
            )
        
        if not test.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Aptitude test is not available"
            )
        
        # Check if user has already attempted this test
        attempts = current_user.aptitude_attempts.get(test_id, 0)
        max_attempts = test.config.max_attempts or 3
        
        if attempts >= max_attempts:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Maximum attempts ({max_attempts}) reached for this test"
            )
        
        return {
            "test": {
                "_id": str(test.id),  # Frontend expects _id
                "title": test.title,
                "description": test.description,
                "type": test.type,  # Frontend expects type
                "config": {
                    "totalQuestions": len(test.questions),
                    "timeLimit": test.config.time_limit,  # In seconds
                    "passingScore": test.config.passing_score,
                    "maxAttempts": test.config.max_attempts
                },
                "usageStats": {
                    "totalAttempts": test.usage_stats.total_attempts,
                    "averageScore": test.usage_stats.average_score,
                    "completionRate": test.usage_stats.completion_rate
                },
                "questions": [
                    {
                        "id": f"q_{i+1}",
                        "questionText": q.question_text,
                        "options": [
                            {"text": opt.text} for opt in q.options
                        ],
                        "category": q.category.value if hasattr(q.category, 'value') else str(q.category),
                        "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
                        "estimatedTime": q.estimated_time
                    } for i, q in enumerate(test.questions)
                ],
                "attempts_remaining": max_attempts - attempts,
                "user_attempts": attempts
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching aptitude test {test_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch aptitude test"
        )

# Additional endpoints for test functionality
@router.post("/{test_id}/start")
async def start_aptitude_test(
    test_id: str,
    current_user: User = Depends(get_current_user)
):
    """Start an aptitude test"""
    try:
        # Get the test
        test = await AptitudeTest.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aptitude test not found"
            )
        
        if not test.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Aptitude test is not available"
            )
        
        # Check if user has already attempted this test
        attempts = current_user.aptitude_attempts.get(test_id, 0)
        max_attempts = test.config.max_attempts or 3
        
        if attempts >= max_attempts:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Maximum attempts ({max_attempts}) reached for this test"
            )
        
        # Return test data for starting
        return {
            "test": {
                "_id": str(test.id),
                "title": test.title,
                "description": test.description,
                "type": test.type,
                "config": {
                    "totalQuestions": len(test.questions),
                    "timeLimit": test.config.time_limit,
                    "passingScore": test.config.passing_score,
                    "maxAttempts": test.config.max_attempts
                },
                "usageStats": {
                    "totalAttempts": test.usage_stats.total_attempts,
                    "averageScore": test.usage_stats.average_score,
                    "completionRate": test.usage_stats.completion_rate
                },
                "questions": [
                    {
                        "id": f"q_{i+1}",
                        "questionText": q.question_text,
                        "options": [
                            {"text": opt.text} for opt in q.options
                        ],
                        "category": q.category.value if hasattr(q.category, 'value') else str(q.category),
                        "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
                        "estimatedTime": q.estimated_time
                    } for i, q in enumerate(test.questions)
                ],
                "attempts_remaining": max_attempts - attempts,
                "user_attempts": attempts
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting aptitude test {test_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start aptitude test: {str(e)}"
        )

@router.post("/{test_id}/answer")
async def submit_answer(
    test_id: str,
    answer_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Submit an answer for an aptitude test"""
    try:
        question_id = answer_data.get("questionId")
        answer = answer_data.get("answer")
        
        if question_id is None or answer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="questionId and answer are required"
            )
        
        # Get the test
        test = await AptitudeTest.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aptitude test not found"
            )
        
        # Here you would typically save the answer to the database
        # For now, just return success
        return {"success": True, "message": "Answer submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting answer for test {test_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )

@router.post("/{test_id}/complete")
async def complete_aptitude_test(
    test_id: str,
    current_user: User = Depends(get_current_user)
):
    """Complete an aptitude test"""
    try:
        # Get the test
        test = await AptitudeTest.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aptitude test not found"
            )
        
        # Calculate actual score based on submitted answers
        # For now, return mock results but save to user history
        total_questions = len(test.questions)
        correct_answers = min(2, total_questions)  # Mock: 2 correct out of total
        score_percentage = (correct_answers / total_questions) * 100
        passing_score = test.config.passing_score or 60.0
        time_spent = 1200  # Mock time in seconds
        
        # Save to user's aptitude history
        from app.models.user import AptitudeHistory, AptitudeAnswer
        from datetime import datetime
        
        # Create mock answers for history
        mock_answers = []
        for i, question in enumerate(test.questions):
            answer = AptitudeAnswer(
                question_id=f"q_{i+1}",
                answer=0 if i < correct_answers else 1,  # Mock correct/incorrect answers
                time_spent=time_spent / total_questions,
                timestamp=datetime.now()
            )
            mock_answers.append(answer)
        
        # Create history entry
        history_entry = AptitudeHistory(
            test_id=str(test.id),
            test_title=test.title,
            test_type=test.type.value if hasattr(test.type, 'value') else str(test.type),
            score=score_percentage,
            passed=score_percentage >= passing_score,
            completed_at=datetime.now(),
            time_spent=time_spent,
            answers=mock_answers
        )
        
        # Add to user's aptitude history
        if not current_user.aptitude_history:
            current_user.aptitude_history = []
        current_user.aptitude_history.append(history_entry)
        
        # Update attempt count
        if not current_user.aptitude_attempts:
            current_user.aptitude_attempts = {}
        current_user.aptitude_attempts[str(test.id)] = current_user.aptitude_attempts.get(str(test.id), 0) + 1
        
        # Save user
        await current_user.save()
        
        results = {
            "score": score_percentage,
            "totalQuestions": total_questions,
            "correctAnswers": correct_answers,
            "timeTaken": time_spent,
            "passed": score_percentage >= passing_score,
            "testType": test.type.value if hasattr(test.type, 'value') else str(test.type)
        }
        
        return {
            "results": results,
            "test": {
                "_id": str(test.id),
                "title": test.title,
                "type": test.type.value if hasattr(test.type, 'value') else str(test.type)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing aptitude test {test_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete aptitude test: {str(e)}"
        )

