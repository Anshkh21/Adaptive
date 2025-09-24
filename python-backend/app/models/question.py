"""
Question model for Python backend
Equivalent to Node.js Question model
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

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

class QuestionType(str, Enum):
    CONCEPTUAL = "conceptual"
    PROBLEM_SOLVING = "problem-solving"
    ANALYTICAL = "analytical"
    APPLICATION = "application"

class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class QuestionOption(BaseModel):
    text: str
    is_correct: bool = False

class Psychometrics(BaseModel):
    discrimination: float = Field(0.5, ge=0, le=1)
    difficulty: float = Field(0.5, ge=0, le=1)
    guessing: float = Field(0.25, ge=0, le=1)
    upper_asymptote: float = Field(1.0, ge=0, le=1)

class UsageStats(BaseModel):
    times_used: int = 0
    correct_answers: int = 0
    average_time_spent: float = 0.0
    last_used: Optional[datetime] = None

class AIGenerated(BaseModel):
    is_ai_generated: bool = False
    generation_prompt: Optional[str] = None
    generation_model: Optional[str] = None
    generation_timestamp: Optional[datetime] = None

class Question(Document):
    question_text: str
    options: List[QuestionOption] = Field(..., min_items=2, max_items=4)
    correct_answer: int = Field(..., ge=0, le=3)
    explanation: Optional[str] = None
    difficulty: Difficulty
    difficulty_score: float = Field(50.0, ge=0, le=100)
    subject: str
    topic: str
    subtopic: Optional[str] = None
    tags: List[str] = []
    cognitive_level: CognitiveLevel = CognitiveLevel.UNDERSTAND
    question_type: QuestionType = QuestionType.CONCEPTUAL
    estimated_time: int = 60  # in seconds
    
    # Psychometric properties
    psychometrics: Psychometrics = Psychometrics()
    
    # Usage statistics
    usage_stats: UsageStats = UsageStats()
    
    # AI Generation metadata
    ai_generated: AIGenerated = AIGenerated()
    
    # Quality metrics
    quality_score: float = Field(50.0, ge=0, le=100)
    review_status: ReviewStatus = ReviewStatus.PENDING
    reviewed_by: Optional[str] = None  # User ID
    review_comments: Optional[str] = None
    
    # Version control
    version: int = 1
    previous_versions: List[str] = []  # Question IDs
    is_active: bool = True
    created_by: str  # User ID
    target_branch: str = ""  # Empty means all branches
    target_year: str = ""  # Empty means all years

    class Settings:
        name = "questions"
        indexes = [
            "subject",
            "topic",
            "difficulty",
            "difficulty_score",
            "cognitive_level",
            "psychometrics.difficulty",
            "usage_stats.times_used",
            "is_active"
        ]

    def calculate_effectiveness(self) -> float:
        """Calculate question effectiveness"""
        if self.usage_stats.times_used == 0:
            return 0.0
        
        accuracy = self.usage_stats.correct_answers / self.usage_stats.times_used
        discrimination = self.psychometrics.discrimination
        difficulty = self.psychometrics.difficulty
        
        # Effectiveness formula: balances accuracy, discrimination, and appropriate difficulty
        return (accuracy * 0.4 + discrimination * 0.4 + (1 - abs(difficulty - 0.5)) * 0.2) * 100

    def update_usage_stats(self, is_correct: bool, time_spent: float):
        """Update usage statistics"""
        self.usage_stats.times_used += 1
        if is_correct:
            self.usage_stats.correct_answers += 1
        
        # Update average time spent
        total_time = self.usage_stats.average_time_spent * (self.usage_stats.times_used - 1) + time_spent
        self.usage_stats.average_time_spent = total_time / self.usage_stats.times_used
        
        self.usage_stats.last_used = datetime.now()

    def update_psychometrics(self, responses: List[Dict[str, Any]]):
        """Update psychometric properties"""
        if not responses:
            return
        
        correct_responses = sum(1 for r in responses if r.get('is_correct', False))
        total_responses = len(responses)
        
        # Update difficulty (proportion of correct responses)
        self.psychometrics.difficulty = correct_responses / total_responses
        
        # Calculate discrimination (difference between high and low performers)
        sorted_responses = sorted(responses, key=lambda x: x.get('user_ability', 0), reverse=True)
        top_third = (len(sorted_responses) + 2) // 3  # Ceiling division
        bottom_third = len(sorted_responses) // 3  # Floor division
        
        top_correct = sum(1 for r in sorted_responses[:top_third] if r.get('is_correct', False))
        bottom_correct = sum(1 for r in sorted_responses[-bottom_third:] if r.get('is_correct', False))
        
        if top_third > 0 and bottom_third > 0:
            self.psychometrics.discrimination = (top_correct / top_third) - (bottom_correct / bottom_third)

    def get_adaptive_difficulty(self) -> float:
        """Get question difficulty score for adaptive algorithm"""
        # Combine multiple factors for adaptive difficulty
        base_difficulty = self.difficulty_score
        psychometric_difficulty = self.psychometrics.difficulty * 100
        usage_accuracy = (self.usage_stats.correct_answers / self.usage_stats.times_used * 100) if self.usage_stats.times_used > 0 else 50
        
        # Weighted average
        return (base_difficulty * 0.4 + psychometric_difficulty * 0.4 + usage_accuracy * 0.2)

    @property
    def correct_option_text(self) -> str:
        """Get the text of the correct option"""
        if 0 <= self.correct_answer < len(self.options):
            return self.options[self.correct_answer].text
        return ""

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
