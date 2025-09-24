"""
User model for Python backend
Equivalent to Node.js User model
"""

from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
import bcrypt

class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

class AcademicLevel(str, Enum):
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    PHD = "phd"

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"

class StudentProfile(BaseModel):
    academic_level: AcademicLevel = AcademicLevel.UNDERGRADUATE
    specialization: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0, le=10)
    previous_assessments: List[str] = []  # Assessment IDs
    skill_level: Dict[str, float] = {}  # Skill areas to proficiency levels (0-100)
    learning_style: Optional[LearningStyle] = None

class PerformanceMetrics(BaseModel):
    total_assessments: int = 0
    average_score: float = 0.0
    improvement_rate: float = 0.0
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommended_topics: List[str] = []

class AptitudeAnswer(BaseModel):
    question_id: str
    answer: int
    time_spent: float
    timestamp: datetime

class CurrentAptitudeTest(BaseModel):
    test_id: Optional[str] = None
    user_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    answers: List[AptitudeAnswer] = []
    score: Optional[float] = None
    status: Optional[str] = None
    time_spent: Optional[float] = None

class AptitudeHistory(BaseModel):
    test_id: str
    test_title: str
    test_type: str
    score: float
    passed: bool
    completed_at: datetime
    time_spent: float
    answers: List[AptitudeAnswer]

class User(Document):
    email: Indexed(EmailStr, unique=True)
    password: str = Field(..., min_length=6)
    first_name: str
    last_name: str
    role: UserRole = UserRole.STUDENT
    institution: str
    department: Optional[str] = None
    year: Optional[str] = None
    roll_number: Optional[Indexed(str, unique=True)] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    
    # Student-specific fields
    student_profile: Optional[StudentProfile] = None
    
    # Performance tracking
    performance_metrics: PerformanceMetrics = PerformanceMetrics()
    
    # Instructor assignment
    assigned_instructor: Optional[str] = None  # User ID
    
    # Class/Batch information
    batch: str = ""
    section: str = ""
    
    # Aptitude test fields
    aptitude_attempts: Dict[str, int] = {}  # testId to attempt count
    current_aptitude_test: Optional[CurrentAptitudeTest] = None
    aptitude_history: List[AptitudeHistory] = []
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "roll_number",
            "institution",
            "role"
        ]

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    async def set_password(self, password: str):
        """Set hashed password"""
        self.password = self.hash_password(password)

    async def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def get_skill_level(self, skill_area: str) -> float:
        """Get user's current skill level for a specific area"""
        if not self.student_profile or not self.student_profile.skill_level:
            return 0.0
        return self.student_profile.skill_level.get(skill_area, 0.0)

    def update_skill_level(self, skill_area: str, performance: float, difficulty: float) -> float:
        """Update skill level based on performance"""
        if not self.student_profile:
            self.student_profile = StudentProfile()
        
        if not self.student_profile.skill_level:
            self.student_profile.skill_level = {}
        
        current_level = self.get_skill_level(skill_area)
        adjustment = (performance - 0.5) * difficulty * 10  # Adjust based on performance
        new_level = max(0.0, min(100.0, current_level + adjustment))
        
        self.student_profile.skill_level[skill_area] = new_level
        return new_level

    def get_overall_proficiency(self) -> float:
        """Calculate overall proficiency"""
        if not self.student_profile or not self.student_profile.skill_level:
            return 0.0
        
        levels = list(self.student_profile.skill_level.values())
        if not levels:
            return 0.0
        
        return sum(levels) / len(levels)

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
