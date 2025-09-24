"""
Gemini AI service for Python backend
Enhanced version of Node.js AI question generator
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai
from pydantic import BaseModel

class QuestionOption(BaseModel):
    text: str
    is_correct: bool = False

class GeneratedQuestion(BaseModel):
    question_text: str
    options: List[QuestionOption]
    correct_answer: int
    explanation: str
    difficulty: str
    difficulty_score: float
    subject: str
    topic: str
    subtopic: Optional[str] = None
    tags: List[str] = []
    cognitive_level: str = "understand"
    question_type: str = "conceptual"
    estimated_time: int = 60
    skill_tested: str

class GeminiQuestionGenerator:
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.fallback_enabled = True
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"❌ Gemini AI initialization failed: {e}")
                self.model = None
        else:
            print("⚠️ GEMINI_API_KEY not found, using fallback mode")
            self.model = None

    async def generate_question(
        self,
        subject: str,
        topic: str,
        difficulty: str = "medium",
        subtopic: Optional[str] = None,
        skill_tested: Optional[str] = None
    ) -> Optional[GeneratedQuestion]:
        """Generate a question using Gemini AI"""
        
        if not self.model:
            return await self.generate_fallback_question(subject, topic, difficulty, subtopic, skill_tested)
        
        try:
            # Create prompt for question generation
            prompt = self._create_question_prompt(subject, topic, difficulty, subtopic, skill_tested)
            
            # Generate question using Gemini
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            if response and response.text:
                # Parse the response
                question_data = self._parse_gemini_response(response.text, subject, topic, difficulty)
                if question_data:
                    return GeneratedQuestion(**question_data)
            
            # If parsing fails, use fallback
            return await self.generate_fallback_question(subject, topic, difficulty, subtopic, skill_tested)
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return await self.generate_fallback_question(subject, topic, difficulty, subtopic, skill_tested)

    def _create_question_prompt(
        self,
        subject: str,
        topic: str,
        difficulty: str,
        subtopic: Optional[str] = None,
        skill_tested: Optional[str] = None
    ) -> str:
        """Create a detailed prompt for question generation"""
        
        difficulty_descriptions = {
            "easy": "basic understanding and recall",
            "medium": "application and analysis",
            "hard": "complex problem-solving and evaluation"
        }
        
        prompt = f"""
Generate a high-quality multiple-choice question for an educational assessment platform.

Subject: {subject}
Topic: {topic}
Difficulty: {difficulty} ({difficulty_descriptions.get(difficulty, 'medium')})
Subtopic: {subtopic or 'General'}
Skill Tested: {skill_tested or 'General knowledge'}

Requirements:
1. Create a clear, well-structured question
2. Provide exactly 4 options (A, B, C, D)
3. Only one option should be correct
4. Include a detailed explanation
5. Make it appropriate for {difficulty} level
6. Ensure the question tests practical understanding

Format your response as JSON:
{{
    "question_text": "Your question here",
    "options": [
        {{"text": "Option A", "is_correct": false}},
        {{"text": "Option B", "is_correct": false}},
        {{"text": "Option C", "is_correct": true}},
        {{"text": "Option D", "is_correct": false}}
    ],
    "correct_answer": 2,
    "explanation": "Detailed explanation of why the correct answer is right",
    "difficulty_score": 75,
    "tags": ["tag1", "tag2"],
    "skill_tested": "Specific skill being tested"
}}

Generate the question now:
"""
        return prompt

    def _parse_gemini_response(self, response_text: str, subject: str, topic: str, difficulty: str) -> Optional[Dict[str, Any]]:
        """Parse Gemini response and extract question data"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                question_data = json.loads(json_str)
                
                # Validate and clean the data
                if self._validate_question_data(question_data):
                    # Add missing fields
                    question_data.update({
                        "subject": subject,
                        "topic": topic,
                        "difficulty": difficulty,
                        "cognitive_level": "understand",
                        "question_type": "conceptual",
                        "estimated_time": 60
                    })
                    return question_data
            
            return None
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"❌ Failed to parse Gemini response: {e}")
            return None

    def _validate_question_data(self, data: Dict[str, Any]) -> bool:
        """Validate question data structure"""
        required_fields = ["question_text", "options", "correct_answer", "explanation"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate options
        if not isinstance(data["options"], list) or len(data["options"]) != 4:
            return False
        
        # Validate correct answer index
        correct_idx = data["correct_answer"]
        if not isinstance(correct_idx, int) or correct_idx < 0 or correct_idx > 3:
            return False
        
        return True

    async def generate_fallback_question(
        self,
        subject: str,
        topic: str,
        difficulty: str = "medium",
        subtopic: Optional[str] = None,
        skill_tested: Optional[str] = None
    ) -> GeneratedQuestion:
        """Generate fallback question when Gemini is not available"""
        
        # Fallback question templates
        templates = {
            "Computer Science": {
                "Object-Oriented Programming": {
                    "easy": {
                        "question": "What is the main principle of Object-Oriented Programming?",
                        "options": [
                            "Procedural programming",
                            "Encapsulation",
                            "Linear programming",
                            "Functional programming"
                        ],
                        "correct": 1,
                        "explanation": "Encapsulation is a fundamental principle of OOP that bundles data and methods together."
                    },
                    "medium": {
                        "question": "Which OOP concept allows a class to inherit properties from another class?",
                        "options": [
                            "Polymorphism",
                            "Inheritance",
                            "Encapsulation",
                            "Abstraction"
                        ],
                        "correct": 1,
                        "explanation": "Inheritance allows a class to inherit properties and methods from a parent class."
                    },
                    "hard": {
                        "question": "In Java, what happens when you override a method with a more restrictive access modifier?",
                        "options": [
                            "It compiles successfully",
                            "It throws a runtime exception",
                            "It causes a compilation error",
                            "It works but with reduced functionality"
                        ],
                        "correct": 2,
                        "explanation": "Overriding with a more restrictive access modifier causes a compilation error in Java."
                    }
                },
                "Database Fundamentals": {
                    "easy": {
                        "question": "What does SQL stand for?",
                        "options": [
                            "Structured Query Language",
                            "Simple Query Language",
                            "Standard Query Language",
                            "System Query Language"
                        ],
                        "correct": 0,
                        "explanation": "SQL stands for Structured Query Language, used for managing relational databases."
                    },
                    "medium": {
                        "question": "Which SQL command is used to retrieve data from a database?",
                        "options": [
                            "INSERT",
                            "UPDATE",
                            "SELECT",
                            "DELETE"
                        ],
                        "correct": 2,
                        "explanation": "SELECT is used to retrieve data from database tables."
                    },
                    "hard": {
                        "question": "What is the difference between INNER JOIN and LEFT JOIN?",
                        "options": [
                            "No difference",
                            "INNER JOIN returns only matching rows, LEFT JOIN returns all rows from left table",
                            "LEFT JOIN is faster than INNER JOIN",
                            "INNER JOIN is used for updates, LEFT JOIN for selects"
                        ],
                        "correct": 1,
                        "explanation": "INNER JOIN returns only matching rows, while LEFT JOIN returns all rows from the left table and matching rows from the right table."
                    }
                }
            }
        }
        
        # Get template based on subject and topic
        template_data = None
        if subject in templates and topic in templates[subject]:
            template_data = templates[subject][topic].get(difficulty, templates[subject][topic]["medium"])
        
        # Default fallback if no template found
        if not template_data:
            template_data = {
                "question": f"What is a key concept in {topic}?",
                "options": [
                    "Option A",
                    "Option B", 
                    "Option C",
                    "Option D"
                ],
                "correct": 1,
                "explanation": f"This question tests understanding of {topic} concepts."
            }
        
        # Create options
        options = []
        for i, option_text in enumerate(template_data["options"]):
            options.append(QuestionOption(
                text=option_text,
                is_correct=(i == template_data["correct"])
            ))
        
        # Calculate difficulty score
        difficulty_scores = {"easy": 30, "medium": 60, "hard": 85}
        difficulty_score = difficulty_scores.get(difficulty, 60)
        
        return GeneratedQuestion(
            question_text=template_data["question"],
            options=options,
            correct_answer=template_data["correct"],
            explanation=template_data["explanation"],
            difficulty=difficulty,
            difficulty_score=difficulty_score,
            subject=subject,
            topic=topic,
            subtopic=subtopic or "General",
            tags=[subject.lower(), topic.lower().replace(" ", "-")],
            cognitive_level="understand",
            question_type="conceptual",
            estimated_time=60,
            skill_tested=skill_tested or f"{topic} knowledge"
        )

    async def generate_multiple_questions(
        self,
        subject: str,
        topics: List[str],
        count: int,
        difficulty_distribution: Dict[str, int] = None
    ) -> List[GeneratedQuestion]:
        """Generate multiple questions for an assessment"""
        
        if not difficulty_distribution:
            difficulty_distribution = {"easy": count//3, "medium": count//3, "hard": count//3}
        
        questions = []
        
        for i in range(count):
            # Select topic and difficulty
            topic = topics[i % len(topics)]
            difficulty = "medium"  # Default
            
            # Assign difficulty based on distribution
            if i < difficulty_distribution.get("easy", 0):
                difficulty = "easy"
            elif i < difficulty_distribution.get("easy", 0) + difficulty_distribution.get("medium", 0):
                difficulty = "medium"
            else:
                difficulty = "hard"
            
            # Generate question
            question = await self.generate_question(subject, topic, difficulty)
            if question:
                questions.append(question)
        
        return questions

# Global instance
gemini_generator = GeminiQuestionGenerator()
