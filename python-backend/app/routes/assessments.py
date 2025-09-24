"""
Assessment routes for Python backend
Equivalent to Node.js assessment routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random
from beanie.operators import Or

from app.models.user import User
from app.models.assessment import Assessment, AssessmentType, AssessmentStatus, AssessmentConfig, AssessmentQuestion
from app.models.question import Question, Difficulty
from app.routes.auth import get_current_user
from app.ai.gemini_service import GeminiQuestionGenerator

router = APIRouter()

class CreateAssessmentRequest(BaseModel):
    assessmentType: AssessmentType = Field(alias="assessmentType")
    subject: str
    topics: List[str]
    config: AssessmentConfig
    
    class Config:
        populate_by_name = True

class AssessmentResponse(BaseModel):
    id: str
    title: str
    assessment_type: AssessmentType
    subject: str
    topics: List[str]
    config: AssessmentConfig
    status: AssessmentStatus
    questions: List[Dict[str, Any]]
    created_at: datetime

class AssessmentListResponse(BaseModel):
    assessments: List[Dict[str, Any]]
    incomplete_assessments: List[Dict[str, Any]]

@router.post("/create", response_model=AssessmentResponse)
async def create_assessment(
    request: CreateAssessmentRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new assessment"""
    # Only students can create assessments
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can create assessments"
        )
    
    # Check for incomplete assessments and auto-submit stale ones
    incomplete_assessments = await Assessment.find(
        Assessment.user_id == str(current_user.id),
        Or(
            Assessment.status == AssessmentStatus.NOT_STARTED,
            Assessment.status == AssessmentStatus.IN_PROGRESS
        )
    ).to_list()
    
    # Auto-submit assessments that are stale (inactive for >24 hours)
    stale_cutoff = datetime.now() - timedelta(hours=24)
    for assessment in incomplete_assessments:
        if assessment.last_accessed_at < stale_cutoff:
            await auto_submit_assessment(assessment)
    
    # Generate questions based on topics
    gemini_service = GeminiQuestionGenerator()
    generated_questions = await gemini_service.generate_multiple_questions(
        subject=request.subject,
        topics=request.topics,
        count=request.config.totalQuestions
    )
    
    # Convert generated questions to AssessmentQuestion format
    questions = []
    for i, q in enumerate(generated_questions):
        question = AssessmentQuestion(
            question_id=f"q_{i+1}",
            order=i + 1,
            time_spent=0.0,
            is_answered=False,
            selected_answer=None,
            is_correct=None,
            difficulty=q.get('difficulty', Difficulty.MEDIUM),
            adaptive_reason=f"Generated for {request.subject} - {request.topics[0] if request.topics else 'General'}"
        )
        questions.append(question)
    
    # Create assessment
    assessment = Assessment(
        user_id=str(current_user.id),
        assessment_type=request.assessmentType,
        title=f"{request.assessmentType.replace('-', ' ').title()} - {request.subject}",
        subject=request.subject,
        topics=request.topics,
        config=request.config,
        questions=questions,
        status=AssessmentStatus.NOT_STARTED
    )
    
    await assessment.insert()
    
    # Return assessment with questions (without correct answers)
    questions_for_response = []
    for i, q in enumerate(generated_questions):
        question_data = {
            "id": f"q_{i+1}",
            "order": i + 1,
            "question_text": q.get('question', 'Sample question text'),
            "options": q.get('options', [
                {"text": "Option A", "is_correct": False},
                {"text": "Option B", "is_correct": False},
                {"text": "Option C", "is_correct": False},
                {"text": "Option D", "is_correct": False}
            ]),
            "difficulty": q.get('difficulty', Difficulty.MEDIUM),
            "estimated_time": q.get('estimated_time', 60)
        }
        questions_for_response.append(question_data)
    
    return AssessmentResponse(
        id=str(assessment.id),
        title=assessment.title,
        assessment_type=assessment.assessment_type,
        subject=assessment.subject,
        topics=assessment.topics,
        config=assessment.config,
        status=assessment.status,
        questions=questions_for_response,
        created_at=datetime.now()  # Use current time since Assessment doesn't have created_at
    )

@router.get("", response_model=AssessmentListResponse)
@router.get("/", response_model=AssessmentListResponse)
async def get_user_assessments(current_user: User = Depends(get_current_user)):
    """Get user's assessments"""
    try:
        print(f"Getting assessments for user: {current_user.id}, role: {current_user.role}")
        
        # Only students can view their assessments
        if current_user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can view assessments"
            )
        
        # Get all assessments for the user
        assessments = await Assessment.find(
            Assessment.user_id == str(current_user.id)
        ).sort(-Assessment.id).limit(10).to_list()  # Sort by ID instead of created_at
        
        print(f"Found {len(assessments)} assessments")
        
        # Get incomplete assessments
        incomplete_assessments = await Assessment.find(
            Assessment.user_id == str(current_user.id),
            Or(
                Assessment.status == AssessmentStatus.NOT_STARTED,
                Assessment.status == AssessmentStatus.IN_PROGRESS
            )
        ).to_list()
        
        print(f"Found {len(incomplete_assessments)} incomplete assessments")
        
        # Format response
        assessment_list = []
        for assessment in assessments:
            assessment_data = {
                "id": str(assessment.id),
                "title": assessment.title,
                "assessment_type": assessment.assessment_type,
                "subject": assessment.subject,
                "status": assessment.status,
                "created_at": datetime.now(),  # Use current time since Assessment doesn't have created_at
                "results": assessment.results.dict() if assessment.results else None
            }
            assessment_list.append(assessment_data)
        
        incomplete_list = []
        for assessment in incomplete_assessments:
            incomplete_data = {
                "id": str(assessment.id),
                "title": assessment.title,
                "assessment_type": assessment.assessment_type,
                "subject": assessment.subject,
                "status": assessment.status,
                "last_accessed_at": assessment.last_accessed_at,
                "progress": assessment.get_progress()
            }
            incomplete_list.append(incomplete_data)
        
        return AssessmentListResponse(
            assessments=assessment_list,
            incomplete_assessments=incomplete_list
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_user_assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessments: {str(e)}"
        )

@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific assessment"""
    assessment = await Assessment.get(assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Check if user owns this assessment
    if assessment.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "id": str(assessment.id),
        "title": assessment.title,
        "assessment_type": assessment.assessment_type,
        "subject": assessment.subject,
        "topics": assessment.topics,
        "config": assessment.config.dict(),
        "status": assessment.status,
        "results": assessment.results.dict() if assessment.results else None,
        "created_at": datetime.now()  # Use current time since Assessment doesn't have created_at
    }

async def generate_questions_for_assessment(
    subject: str,
    topics: List[str],
    total_questions: int
) -> List[Dict[str, Any]]:
    """Generate questions for assessment (placeholder implementation)"""
    # This is a simplified version - in reality, you'd query the database
    # or use AI to generate questions based on the topics
    
    questions = []
    for i in range(total_questions):
        question_data = {
            "question_id": f"q_{i+1}",
            "order": i + 1,
            "time_spent": 0.0,
            "is_answered": False,
            "selected_answer": None,
            "is_correct": None,
            "difficulty": random.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]),
            "adaptive_reason": f"Selected for {subject} assessment"
        }
        questions.append(question_data)
    
    return questions

async def auto_submit_assessment(assessment: Assessment):
    """Auto-submit an incomplete assessment"""
    # Calculate score for answered questions
    answered_questions = [q for q in assessment.questions if q.is_answered]
    correct_answers = sum(1 for q in answered_questions if q.is_correct)
    
    # Update results
    assessment.results.total_questions = len(assessment.questions)
    assessment.results.answered_questions = len(answered_questions)
    assessment.results.correct_answers = correct_answers
    assessment.results.incorrect_answers = len(answered_questions) - correct_answers
    assessment.results.skipped_questions = len(assessment.questions) - len(answered_questions)
    
    if len(answered_questions) > 0:
        assessment.results.percentage = (correct_answers / len(answered_questions)) * 100
    else:
        assessment.results.percentage = 0
    
    assessment.results.score = assessment.results.percentage
    assessment.results.passed = assessment.results.percentage >= assessment.config.passingScore
    
    # Update status
    assessment.status = AssessmentStatus.COMPLETED
    assessment.end_time = datetime.now()
    assessment.auto_submitted = True
    assessment.completion_reason = "auto-submitted"
    
    await assessment.save()
