"""
AptitudeTest model for Python backend
Equivalent to Node.js AptitudeTest model
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class AptitudeTestType(str, Enum):
    QUANTITATIVE = "quantitative"
    LOGICAL = "logical"
    VERBAL = "verbal"
    COMPREHENSIVE = "comprehensive"

class QuestionCategory(str, Enum):
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    LOGICAL_REASONING = "logical-reasoning"
    VERBAL_REASONING = "verbal-reasoning"
    ANALYTICAL = "analytical"
    PATTERN_RECOGNITION = "pattern-recognition"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class CognitiveLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class AptitudeQuestionOption(BaseModel):
    text: str
    is_correct: bool = False

class AptitudeQuestion(BaseModel):
    question_text: str
    options: List[AptitudeQuestionOption] = Field(..., min_items=2, max_items=4)
    correct_answer: int = Field(..., ge=0, le=3)
    explanation: Optional[str] = None
    category: QuestionCategory
    difficulty: Difficulty
    difficulty_score: float = Field(50.0, ge=0, le=100)
    estimated_time: int = 60  # in seconds
    skill_tested: str
    cognitive_level: CognitiveLevel = CognitiveLevel.APPLY

class TestSection(BaseModel):
    name: str
    questions: int
    time_limit: int  # in seconds

class AptitudeTestConfig(BaseModel):
    total_questions: int = 30
    time_limit: int = 1800  # 30 minutes in seconds
    passing_score: float = 60.0  # 60%
    max_attempts: int = 3
    sections: List[TestSection] = []

class UsageStats(BaseModel):
    total_attempts: int = 0
    average_score: float = 0.0
    completion_rate: float = 0.0

class AptitudeTest(Document):
    title: str
    description: Optional[str] = None
    type: AptitudeTestType
    questions: List[AptitudeQuestion] = []
    config: AptitudeTestConfig = AptitudeTestConfig()
    
    # Usage statistics
    usage_stats: UsageStats = UsageStats()
    
    is_active: bool = True
    created_by: str  # User ID

    class Settings:
        name = "aptitude_tests"
        indexes = [
            "type",
            "is_active",
            "questions.category",
            "questions.difficulty"
        ]

    def calculate_effectiveness(self) -> float:
        """Calculate test effectiveness"""
        if self.usage_stats.total_attempts == 0:
            return 0.0
        
        completion_rate = self.usage_stats.completion_rate
        average_score = self.usage_stats.average_score
        
        # Effectiveness formula: balances completion rate and average score
        return (completion_rate * 0.4 + average_score * 0.6)

    def update_usage_stats(self, score: float, completed: bool):
        """Update usage statistics"""
        self.usage_stats.total_attempts += 1
        
        # Update average score
        total_score = self.usage_stats.average_score * (self.usage_stats.total_attempts - 1) + score
        self.usage_stats.average_score = total_score / self.usage_stats.total_attempts
        
        # Update completion rate
        total_completed = self.usage_stats.completion_rate * (self.usage_stats.total_attempts - 1) + (1 if completed else 0)
        self.usage_stats.completion_rate = total_completed / self.usage_stats.total_attempts

    def get_questions_by_category(self, category: QuestionCategory) -> List[AptitudeQuestion]:
        """Get questions filtered by category"""
        return [q for q in self.questions if q.category == category]

    def get_questions_by_difficulty(self, difficulty: Difficulty) -> List[AptitudeQuestion]:
        """Get questions filtered by difficulty"""
        return [q for q in self.questions if q.difficulty == difficulty]

    def get_section_questions(self, section_name: str) -> List[AptitudeQuestion]:
        """Get questions for a specific section"""
        # This would need to be implemented based on how sections are structured
        # For now, return all questions
        return self.questions

    @property
    def total_sections(self) -> int:
        """Get total number of sections"""
        return len(self.config.sections)

    @property
    def is_comprehensive(self) -> bool:
        """Check if this is a comprehensive test"""
        return self.type == AptitudeTestType.COMPREHENSIVE

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
