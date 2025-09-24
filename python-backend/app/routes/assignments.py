"""
Assignment routes for Python backend
Equivalent to Node.js assignment routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.routes.auth import get_current_user
from app.models.user import User, UserRole
from app.models.assessment import Assessment, AssessmentStatus

router = APIRouter()

def require_instructor_or_admin(current_user: User = Depends(get_current_user)):
    """Require instructor or admin role"""
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor or admin access required"
        )
    return current_user

@router.get("/my-students")
async def get_my_students(instructor: User = Depends(require_instructor_or_admin)):
    """Get students assigned to an instructor"""
    try:
        students = await User.find(
            User.assigned_instructor == str(instructor.id),
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).to_list()

        # Get recent assessments for each student
        students_with_performance = []
        for student in students:
            recent_assessments = await Assessment.find(
                Assessment.user_id == str(student.id),
                Assessment.status == AssessmentStatus.COMPLETED
            ).sort(-Assessment.end_time).limit(5).to_list()

            student_data = {
                "id": str(student.id),
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "department": student.department,
                "year": student.year,
                "roll_number": student.roll_number,
                "batch": student.batch,
                "section": student.section,
                "performance_metrics": student.performance_metrics.dict() if student.performance_metrics else None,
                "recent_assessments": [
                    {
                        "id": str(assessment.id),
                        "assessment_type": assessment.assessment_type,
                        "subject": assessment.subject,
                        "score": assessment.results.score if assessment.results else None,
                        "completed_at": assessment.end_time,
                        "time_spent": assessment.time_spent
                    }
                    for assessment in recent_assessments
                ]
            }
            students_with_performance.append(student_data)

        return {
            "students": students_with_performance,
            "total_count": len(students_with_performance)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching students: {str(e)}"
        )

@router.get("/student/{student_id}/performance")
async def get_student_performance(
    student_id: str,
    instructor: User = Depends(require_instructor_or_admin)
):
    """Get detailed performance data for a specific student"""
    try:
        # Verify the student is assigned to this instructor
        student = await User.get(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        if (instructor.role != UserRole.ADMIN and 
            student.assigned_instructor != str(instructor.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this student"
            )

        # Get all completed assessments
        assessments = await Assessment.find(
            Assessment.user_id == student_id,
            Assessment.status == AssessmentStatus.COMPLETED
        ).sort(-Assessment.end_time).to_list()

        # Calculate performance metrics
        total_assessments = len(assessments)
        total_score = sum(a.results.score for a in assessments if a.results)
        average_score = total_score / total_assessments if total_assessments > 0 else 0

        # Group by subject
        subject_performance = {}
        for assessment in assessments:
            subject = assessment.subject
            if subject not in subject_performance:
                subject_performance[subject] = {
                    "total": 0,
                    "scores": [],
                    "average": 0
                }
            subject_performance[subject]["total"] += 1
            if assessment.results:
                subject_performance[subject]["scores"].append(assessment.results.score)

        # Calculate averages
        for subject, data in subject_performance.items():
            if data["scores"]:
                data["average"] = sum(data["scores"]) / len(data["scores"])

        return {
            "student": {
                "id": str(student.id),
                "name": f"{student.first_name} {student.last_name}",
                "email": student.email,
                "department": student.department,
                "year": student.year,
                "roll_number": student.roll_number
            },
            "performance": {
                "total_assessments": total_assessments,
                "average_score": average_score,
                "subject_breakdown": subject_performance,
                "recent_assessments": [
                    {
                        "id": str(a.id),
                        "title": a.title,
                        "assessment_type": a.assessment_type,
                        "subject": a.subject,
                        "score": a.results.score if a.results else None,
                        "completed_at": a.end_time,
                        "time_spent": a.time_spent
                    }
                    for a in assessments[:10]  # Last 10 assessments
                ]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching student performance: {str(e)}"
        )

@router.post("/assign-student")
async def assign_student_to_instructor(
    student_id: str,
    instructor_id: str,
    admin_user: User = Depends(get_current_user)
):
    """Assign a student to an instructor (admin only)"""
    if admin_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    try:
        # Verify student exists
        student = await User.get(student_id)
        if not student or student.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        # Verify instructor exists
        instructor = await User.get(instructor_id)
        if not instructor or instructor.role != UserRole.INSTRUCTOR:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instructor not found"
            )

        # Assign student to instructor
        student.assigned_instructor = instructor_id
        await student.save()

        return {
            "message": "Student assigned to instructor successfully",
            "student_id": student_id,
            "instructor_id": instructor_id,
            "student_name": f"{student.first_name} {student.last_name}",
            "instructor_name": f"{instructor.first_name} {instructor.last_name}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning student: {str(e)}"
        )

@router.get("/batch-performance")
async def get_batch_performance(
    batch: str,
    instructor: User = Depends(require_instructor_or_admin)
):
    """Get performance data for all students in a batch"""
    try:
        students = await User.find(
            User.batch == batch,
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).to_list()

        batch_performance = []
        for student in students:
            assessments = await Assessment.find(
                Assessment.user_id == str(student.id),
                Assessment.status == AssessmentStatus.COMPLETED
            ).to_list()

            total_score = sum(a.results.score for a in assessments if a.results)
            average_score = total_score / len(assessments) if assessments else 0

            batch_performance.append({
                "student_id": str(student.id),
                "name": f"{student.first_name} {student.last_name}",
                "roll_number": student.roll_number,
                "total_assessments": len(assessments),
                "average_score": average_score,
                "last_assessment": assessments[0].end_time if assessments else None
            })

        # Sort by average score (descending)
        batch_performance.sort(key=lambda x: x["average_score"], reverse=True)

        return {
            "batch": batch,
            "total_students": len(batch_performance),
            "students": batch_performance,
            "batch_average": sum(s["average_score"] for s in batch_performance) / len(batch_performance) if batch_performance else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching batch performance: {str(e)}"
        )
