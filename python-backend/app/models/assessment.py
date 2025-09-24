"""
Assessment model for Python backend
Equivalent to Node.js Assessment model
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class AssessmentType(str, Enum):
    PRE_ASSESSMENT = "pre-assessment"
    ADAPTIVE_ASSESSMENT = "adaptive-assessment"
    FINAL_ASSESSMENT = "final-assessment"
    PRACTICE = "practice"
    TOPIC_WISE = "topic-wise"
    OVERALL = "overall"

class AssessmentStatus(str, Enum):
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    EXPIRED = "expired"

class CompletionReason(str, Enum):
    USER_COMPLETED = "user-completed"
    TIME_EXPIRED = "time-expired"
    AUTO_SUBMITTED = "auto-submitted"
    NETWORK_ERROR = "network-error"

class QuestionSelectionStrategy(str, Enum):
    RANDOM = "random"
    ADAPTIVE = "adaptive"
    DIFFICULTY_BASED = "difficulty-based"
    TOPIC_BASED = "topic-based"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Grade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C_PLUS = "C+"
    C = "C"
    D = "D"
    F = "F"

class AssessmentConfig(BaseModel):
    totalQuestions: int = Field(alias="totalQuestions")
    timeLimit: int = Field(alias="timeLimit")  # in seconds
    passingScore: float = Field(60.0, alias="passingScore")
    adaptiveEnabled: bool = Field(False, alias="adaptiveEnabled")
    questionSelectionStrategy: QuestionSelectionStrategy = Field(QuestionSelectionStrategy.ADAPTIVE, alias="questionSelectionStrategy")
    
    class Config:
        populate_by_name = True

class AssessmentQuestion(BaseModel):
    question_id: str
    order: int
    time_spent: float = 0.0
    is_answered: bool = False
    selected_answer: Optional[int] = None
    is_correct: Optional[bool] = None
    difficulty: Optional[Difficulty] = None
    adaptive_reason: Optional[str] = None

class NetworkRecoveryAnswer(BaseModel):
    question_id: str
    answer: int
    timestamp: datetime

class NetworkRecoveryData(BaseModel):
    current_question_index: int = 0
    answers: List[NetworkRecoveryAnswer] = []
    time_remaining: int = 0
    last_saved_at: datetime = Field(default_factory=datetime.now)

class AssessmentResults(BaseModel):
    total_questions: int = 0
    answered_questions: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    skipped_questions: int = 0
    score: float = 0.0
    percentage: float = 0.0
    grade: Optional[Grade] = None
    passed: bool = False

class AbilityHistory(BaseModel):
    question_index: int
    ability: float
    timestamp: datetime

class QuestionSelectionLog(BaseModel):
    question_id: str
    reason: str
    difficulty: str
    timestamp: datetime

class AdaptationTrigger(BaseModel):
    trigger: str
    action: str
    timestamp: datetime

class AdaptiveData(BaseModel):
    initial_ability: float = 0.0
    final_ability: float = 0.0
    ability_history: List[AbilityHistory] = []
    question_selection_log: List[QuestionSelectionLog] = []
    adaptation_triggers: List[AdaptationTrigger] = []

class PerformanceAnalysis(BaseModel):
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommended_topics: List[str] = []
    skill_gaps: List[str] = []
    improvement_areas: List[str] = []
    next_steps: List[str] = []

class PsychometricAnalysis(BaseModel):
    reliability: Optional[float] = Field(None, ge=0, le=1)
    validity: Optional[float] = Field(None, ge=0, le=1)
    standard_error: Optional[float] = None
    confidence_interval: Optional[Dict[str, float]] = None

class AssessmentMetadata(BaseModel):
    browser: Optional[str] = None
    device: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

class AssessmentReview(BaseModel):
    reviewed_by: Optional[str] = None  # User ID
    review_comments: Optional[str] = None
    review_date: Optional[datetime] = None
    is_flagged: bool = False
    flag_reason: Optional[str] = None

class Assessment(Document):
    user_id: str = Field(..., description="User ID who took the assessment")
    assessment_type: AssessmentType
    title: str
    description: Optional[str] = None
    subject: str
    topics: List[str] = []
    
    # Assessment configuration
    config: AssessmentConfig
    
    # Questions in the assessment
    questions: List[AssessmentQuestion] = []
    
    # Assessment state
    status: AssessmentStatus = AssessmentStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    time_spent: float = 0.0  # total time in seconds
    last_accessed_at: datetime = Field(default_factory=datetime.now)
    auto_submitted: bool = False
    completion_reason: CompletionReason = CompletionReason.USER_COMPLETED
    
    # Network recovery data
    network_recovery_data: Optional[NetworkRecoveryData] = None
    
    # Results
    results: AssessmentResults = AssessmentResults()
    
    # Adaptive assessment specific data
    adaptive_data: AdaptiveData = AdaptiveData()
    
    # Performance analysis
    performance_analysis: PerformanceAnalysis = PerformanceAnalysis()
    
    # Psychometric analysis
    psychometric_analysis: PsychometricAnalysis = PsychometricAnalysis()
    
    # Metadata
    metadata: Optional[AssessmentMetadata] = None
    
    # Review and feedback
    review: Optional[AssessmentReview] = None

    class Settings:
        name = "assessments"
        indexes = [
            "user_id",
            "status",
            "assessment_type",
            "results.score",
            "created_at"
        ]

    def calculate_score(self) -> AssessmentResults:
        """Calculate assessment score"""
        total_questions = len(self.questions)
        correct_answers = sum(1 for q in self.questions if q.is_correct is True)
        incorrect_answers = sum(1 for q in self.questions if q.is_correct is False)
        answered_questions = sum(1 for q in self.questions if q.is_answered)
        
        self.results.total_questions = total_questions
        self.results.correct_answers = correct_answers
        self.results.incorrect_answers = incorrect_answers
        self.results.answered_questions = answered_questions
        self.results.skipped_questions = total_questions - answered_questions
        
        self.results.percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        self.results.score = self.results.percentage
        
        # Determine grade
        if self.results.percentage >= 90:
            self.results.grade = Grade.A_PLUS
        elif self.results.percentage >= 80:
            self.results.grade = Grade.A
        elif self.results.percentage >= 75:
            self.results.grade = Grade.B_PLUS
        elif self.results.percentage >= 70:
            self.results.grade = Grade.B
        elif self.results.percentage >= 65:
            self.results.grade = Grade.C_PLUS
        elif self.results.percentage >= 60:
            self.results.grade = Grade.C
        elif self.results.percentage >= 50:
            self.results.grade = Grade.D
        else:
            self.results.grade = Grade.F
        
        self.results.passed = self.results.percentage >= self.config.passing_score
        
        return self.results

    def update_ability_estimation(self, question_index: int, is_correct: bool, difficulty: str) -> float:
        """Update adaptive ability estimation"""
        current_ability = self.adaptive_data.final_ability or self.adaptive_data.initial_ability
        
        # Simple ability estimation (can be replaced with more sophisticated IRT)
        adjustment = 0.1 if is_correct else -0.1
        difficulty_factor = 0.5 if difficulty == "easy" else 1.0 if difficulty == "medium" else 1.5
        
        new_ability = current_ability + (adjustment * difficulty_factor)
        
        self.adaptive_data.ability_history.append(AbilityHistory(
            question_index=question_index,
            ability=new_ability,
            timestamp=datetime.now()
        ))
        
        self.adaptive_data.final_ability = new_ability
        return new_ability

    def get_next_question(self) -> Optional[AssessmentQuestion]:
        """Get next question for adaptive assessment"""
        unanswered_questions = [q for q in self.questions if not q.is_answered]
        
        if not unanswered_questions:
            return None
        
        # For adaptive assessment, select based on current ability
        if self.config.adaptive_enabled:
            current_ability = self.adaptive_data.final_ability or self.adaptive_data.initial_ability
            
            # Select question with difficulty closest to current ability
            return min(unanswered_questions, key=lambda q: abs(getattr(q, 'difficulty_score', 0) - current_ability))
        
        # For non-adaptive, return next unanswered question
        return min(unanswered_questions, key=lambda q: q.order)

    def is_expired(self) -> bool:
        """Check if assessment is expired"""
        if not self.start_time:
            return False
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.config.time_limit

    def get_progress(self) -> float:
        """Get assessment progress percentage"""
        total = len(self.questions)
        answered = sum(1 for q in self.questions if q.is_answered)
        return (answered / total * 100) if total > 0 else 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
