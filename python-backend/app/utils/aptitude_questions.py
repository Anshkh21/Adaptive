"""
Aptitude Questions utility for Python backend
Equivalent to Node.js aptitudeQuestions.js
"""

from typing import List, Dict, Any
from app.models.aptitude_test import AptitudeTest, AptitudeTestType, QuestionCategory, Difficulty, CognitiveLevel

# Sample aptitude questions for different categories - CAT Level Difficulty
SAMPLE_APTITUDE_QUESTIONS = {
    "quantitative": [
        {
            "question_text": "A train 150m long crosses a platform 300m long in 20 seconds. If the train's speed is increased by 20%, how long will it take to cross the same platform?",
            "options": [
                {"text": "16.67 seconds", "is_correct": True},
                {"text": "18 seconds", "is_correct": False},
                {"text": "20 seconds", "is_correct": False},
                {"text": "22.5 seconds", "is_correct": False}
            ],
            "correct_answer": 0,
            "explanation": "Original speed = (150+300)/20 = 22.5 m/s. New speed = 22.5 × 1.2 = 27 m/s. Time = 450/27 = 16.67 seconds.",
            "category": "arithmetic",
            "difficulty": "hard",
            "difficulty_score": 80,
            "estimated_time": 120,
            "skill_tested": "Speed, Distance, Time",
            "cognitive_level": "analyze"
        },
        {
            "question_text": "In a mixture of 60 liters, the ratio of milk to water is 3:2. If 20 liters of this mixture is replaced with pure milk, what will be the new ratio of milk to water?",
            "options": [
                {"text": "4:1", "is_correct": True},
                {"text": "3:1", "is_correct": False},
                {"text": "5:2", "is_correct": False},
                {"text": "7:3", "is_correct": False}
            ],
            "correct_answer": 0,
            "explanation": "Original: 36L milk, 24L water. After removing 20L (12L milk, 8L water): 24L milk, 16L water. Adding 20L milk: 44L milk, 16L water. Ratio = 44:16 = 11:4 ≈ 4:1",
            "category": "arithmetic",
            "difficulty": "hard",
            "difficulty_score": 85,
            "estimated_time": 150,
            "skill_tested": "Mixtures and Alligations",
            "cognitive_level": "analyze"
        },
        {
            "question_text": "A sum of money becomes Rs. 13,380 after 3 years and Rs. 20,070 after 6 years at compound interest. What is the sum?",
            "options": [
                {"text": "Rs. 8,920", "is_correct": True},
                {"text": "Rs. 9,500", "is_correct": False},
                {"text": "Rs. 10,000", "is_correct": False},
                {"text": "Rs. 11,200", "is_correct": False}
            ],
            "correct_answer": 0,
            "explanation": "Let P be principal, r be rate. P(1+r)³ = 13380, P(1+r)⁶ = 20070. Dividing: (1+r)³ = 20070/13380 = 1.5. So P = 13380/1.5 = 8920",
            "category": "arithmetic",
            "difficulty": "hard",
            "difficulty_score": 90,
            "estimated_time": 180,
            "skill_tested": "Compound Interest",
            "cognitive_level": "analyze"
        }
    ],
    "logical": [
        {
            "question_text": "In a certain code, 'COMPUTER' is written as 'RFUVQNPC'. How is 'MEDICINE' written in that code?",
            "options": [
                {"text": "MFEDJJOE", "is_correct": True},
                {"text": "EOJDEJFM", "is_correct": False},
                {"text": "MJDJEOFE", "is_correct": False},
                {"text": "EOJDJEFM", "is_correct": False}
            ],
            "correct_answer": 0,
            "explanation": "Each letter is replaced by the letter that comes 1 position before it in the alphabet, and then the word is reversed.",
            "category": "logical-reasoning",
            "difficulty": "hard",
            "difficulty_score": 75,
            "estimated_time": 120,
            "skill_tested": "Coding-Decoding",
            "cognitive_level": "analyze"
        },
        {
            "question_text": "If 'A + B' means 'A is the father of B', 'A - B' means 'A is the mother of B', 'A × B' means 'A is the brother of B', then which of the following means 'C is the uncle of D'?",
            "options": [
                {"text": "C × (A + D)", "is_correct": True},
                {"text": "C + (A × D)", "is_correct": False},
                {"text": "C - (A + D)", "is_correct": False},
                {"text": "C × (A - D)", "is_correct": False}
            ],
            "correct_answer": 0,
            "explanation": "C × (A + D) means C is brother of A, and A is father of D. So C is uncle of D.",
            "category": "logical-reasoning",
            "difficulty": "hard",
            "difficulty_score": 80,
            "estimated_time": 150,
            "skill_tested": "Blood Relations",
            "cognitive_level": "analyze"
        }
    ],
    "verbal": [
        {
            "question_text": "Choose the word that is most nearly opposite in meaning to 'PROLIFIC':",
            "options": [
                {"text": "Barren", "is_correct": True},
                {"text": "Fertile", "is_correct": False},
                {"text": "Abundant", "is_correct": False},
                {"text": "Productive", "is_correct": False}
            ],
            "correct_answer": 0,
            "explanation": "Prolific means producing many works or results. Barren means unproductive or infertile, which is the opposite.",
            "category": "verbal-reasoning",
            "difficulty": "medium",
            "difficulty_score": 70,
            "estimated_time": 60,
            "skill_tested": "Antonyms",
            "cognitive_level": "understand"
        },
        {
            "question_text": "In the following sentence, identify the error: 'Neither the manager nor the employees was present at the meeting.'",
            "options": [
                {"text": "was", "is_correct": True},
                {"text": "Neither", "is_correct": False},
                {"text": "nor", "is_correct": False},
                {"text": "present", "is_correct": False}
            ],
            "correct_answer": 0,
            "explanation": "With 'neither...nor', the verb agrees with the subject closer to it. Since 'employees' is plural, it should be 'were present'.",
            "category": "verbal-reasoning",
            "difficulty": "hard",
            "difficulty_score": 75,
            "estimated_time": 90,
            "skill_tested": "Grammar",
            "cognitive_level": "analyze"
        }
    ]
}

async def create_sample_aptitude_tests():
    """Create sample aptitude tests if they don't exist"""
    try:
        # Check if tests already exist
        existing_tests = await AptitudeTest.find(AptitudeTest.is_active == True).count()
        if existing_tests > 0:
            print("Sample aptitude tests already exist")
            return

        # Create Quantitative Aptitude Test
        quantitative_test = AptitudeTest(
            title="Quantitative Aptitude - CAT Level",
            description="Advanced quantitative reasoning test with CAT-level difficulty",
            type=AptitudeTestType.QUANTITATIVE,
            questions=[
                {
                    "question_text": q["question_text"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q["explanation"],
                    "category": q["category"],
                    "difficulty": q["difficulty"],
                    "difficulty_score": q["difficulty_score"],
                    "estimated_time": q["estimated_time"],
                    "skill_tested": q["skill_tested"],
                    "cognitive_level": q["cognitive_level"]
                }
                for q in SAMPLE_APTITUDE_QUESTIONS["quantitative"]
            ],
            config={
                "total_questions": len(SAMPLE_APTITUDE_QUESTIONS["quantitative"]),
                "time_limit": 1800,  # 30 minutes
                "passing_score": 60.0,
                "max_attempts": 3,
                "sections": [
                    {
                        "name": "Arithmetic",
                        "questions": 3,
                        "time_limit": 1800
                    }
                ]
            },
            is_active=True,
            created_by="system"
        )
        await quantitative_test.insert()

        # Create Logical Reasoning Test
        logical_test = AptitudeTest(
            title="Logical Reasoning - CAT Level",
            description="Advanced logical reasoning test with CAT-level difficulty",
            type=AptitudeTestType.LOGICAL,
            questions=[
                {
                    "question_text": q["question_text"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q["explanation"],
                    "category": q["category"],
                    "difficulty": q["difficulty"],
                    "difficulty_score": q["difficulty_score"],
                    "estimated_time": q["estimated_time"],
                    "skill_tested": q["skill_tested"],
                    "cognitive_level": q["cognitive_level"]
                }
                for q in SAMPLE_APTITUDE_QUESTIONS["logical"]
            ],
            config={
                "total_questions": len(SAMPLE_APTITUDE_QUESTIONS["logical"]),
                "time_limit": 1200,  # 20 minutes
                "passing_score": 60.0,
                "max_attempts": 3,
                "sections": [
                    {
                        "name": "Logical Reasoning",
                        "questions": 2,
                        "time_limit": 1200
                    }
                ]
            },
            is_active=True,
            created_by="system"
        )
        await logical_test.insert()

        # Create Verbal Ability Test
        verbal_test = AptitudeTest(
            title="Verbal Ability - CAT Level",
            description="Advanced verbal ability test with CAT-level difficulty",
            type=AptitudeTestType.VERBAL,
            questions=[
                {
                    "question_text": q["question_text"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q["explanation"],
                    "category": q["category"],
                    "difficulty": q["difficulty"],
                    "difficulty_score": q["difficulty_score"],
                    "estimated_time": q["estimated_time"],
                    "skill_tested": q["skill_tested"],
                    "cognitive_level": q["cognitive_level"]
                }
                for q in SAMPLE_APTITUDE_QUESTIONS["verbal"]
            ],
            config={
                "total_questions": len(SAMPLE_APTITUDE_QUESTIONS["verbal"]),
                "time_limit": 900,  # 15 minutes
                "passing_score": 60.0,
                "max_attempts": 3,
                "sections": [
                    {
                        "name": "Verbal Reasoning",
                        "questions": 2,
                        "time_limit": 900
                    }
                ]
            },
            is_active=True,
            created_by="system"
        )
        await verbal_test.insert()

        # Create Comprehensive Test
        comprehensive_test = AptitudeTest(
            title="Comprehensive Aptitude Test - CAT Level",
            description="Complete aptitude test covering all areas with CAT-level difficulty",
            type=AptitudeTestType.COMPREHENSIVE,
            questions=[
                {
                    "question_text": q["question_text"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q["explanation"],
                    "category": q["category"],
                    "difficulty": q["difficulty"],
                    "difficulty_score": q["difficulty_score"],
                    "estimated_time": q["estimated_time"],
                    "skill_tested": q["skill_tested"],
                    "cognitive_level": q["cognitive_level"]
                }
                for category in SAMPLE_APTITUDE_QUESTIONS.values()
                for q in category
            ],
            config={
                "total_questions": sum(len(category) for category in SAMPLE_APTITUDE_QUESTIONS.values()),
                "time_limit": 3600,  # 60 minutes
                "passing_score": 60.0,
                "max_attempts": 3,
                "sections": [
                    {
                        "name": "Quantitative",
                        "questions": len(SAMPLE_APTITUDE_QUESTIONS["quantitative"]),
                        "time_limit": 1800
                    },
                    {
                        "name": "Logical Reasoning",
                        "questions": len(SAMPLE_APTITUDE_QUESTIONS["logical"]),
                        "time_limit": 1200
                    },
                    {
                        "name": "Verbal Ability",
                        "questions": len(SAMPLE_APTITUDE_QUESTIONS["verbal"]),
                        "time_limit": 900
                    }
                ]
            },
            is_active=True,
            created_by="system"
        )
        await comprehensive_test.insert()

        print("✅ Sample aptitude tests created successfully")
        
    except Exception as e:
        print(f"❌ Error creating sample aptitude tests: {e}")
        raise e
