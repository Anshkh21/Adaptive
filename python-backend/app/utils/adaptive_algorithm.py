"""
Adaptive Algorithm for Python backend
Equivalent to Node.js adaptiveAlgorithm.js
"""

import math
from typing import List, Dict, Any, Optional
import numpy as np

class AdaptiveAlgorithm:
    def __init__(self):
        self.ability_estimation_method = 'IRT'  # Item Response Theory
        self.question_selection_strategy = 'maximum_information'
        self.termination_criteria = {
            'max_questions': 50,
            'min_questions': 10,
            'standard_error_threshold': 0.3,
            'confidence_threshold': 0.95
        }

    def estimate_ability(self, responses: List[Dict], questions: List[Dict]) -> float:
        """Estimate student's ability using Item Response Theory (IRT)"""
        if not responses:
            return 0.0

        # Simple IRT implementation using Newton-Raphson method
        theta = 0.0  # Initial ability estimate
        max_iterations = 50
        tolerance = 0.001

        for iteration in range(max_iterations):
            first_derivative = 0.0
            second_derivative = 0.0

            for i, response in enumerate(responses):
                if i >= len(questions):
                    continue
                    
                question = questions[i]
                a = question.get('discrimination', 0.5)
                b = question.get('difficulty', 0.5)
                c = question.get('guessing', 0.25)
                d = question.get('upper_asymptote', 1.0)

                # Probability of correct response
                z = a * (theta - b)
                p = c + (d - c) / (1 + math.exp(-z))

                # First and second derivatives
                pq = p * (1 - p)
                first_deriv = a * (response.get('is_correct', 0) - p) * (d - c) / pq
                second_deriv = -a * a * (d - c) * (d - c) / (pq * pq)

                first_derivative += first_deriv
                second_derivative += second_deriv

            if abs(second_derivative) < tolerance:
                break

            # Newton-Raphson update
            new_theta = theta - first_derivative / second_derivative

            if abs(new_theta - theta) < tolerance:
                break

            theta = new_theta

        return theta

    def calculate_information(self, theta: float, question: Dict) -> float:
        """Calculate Fisher information for a question at given ability level"""
        a = question.get('discrimination', 0.5)
        b = question.get('difficulty', 0.5)
        c = question.get('guessing', 0.25)
        d = question.get('upper_asymptote', 1.0)

        z = a * (theta - b)
        p = c + (d - c) / (1 + math.exp(-z))

        # Fisher information
        information = (a * a * (d - c) * (d - c)) / (p * (1 - p))

        return information

    def select_next_question(self, 
                           current_ability: float, 
                           available_questions: List[Dict], 
                           answered_questions: List[str]) -> Optional[Dict]:
        """Select the next question based on current ability estimate"""
        if not available_questions:
            return None

        # Filter out already answered questions
        unanswered = [q for q in available_questions if q.get('id') not in answered_questions]
        
        if not unanswered:
            return None

        if self.question_selection_strategy == 'maximum_information':
            # Select question with maximum information at current ability
            best_question = None
            max_information = 0

            for question in unanswered:
                information = self.calculate_information(current_ability, question)
                if information > max_information:
                    max_information = information
                    best_question = question

            return best_question

        elif self.question_selection_strategy == 'closest_difficulty':
            # Select question with difficulty closest to current ability
            best_question = None
            min_distance = float('inf')

            for question in unanswered:
                difficulty = question.get('difficulty_score', 50)
                distance = abs(difficulty - current_ability)
                if distance < min_distance:
                    min_distance = distance
                    best_question = question

            return best_question

        else:
            # Random selection as fallback
            return random.choice(unanswered)

    def calculate_standard_error(self, responses: List[Dict], questions: List[Dict]) -> float:
        """Calculate standard error of ability estimate"""
        if not responses:
            return 1.0

        theta = self.estimate_ability(responses, questions)
        information_sum = 0.0

        for i, response in enumerate(responses):
            if i < len(questions):
                information = self.calculate_information(theta, questions[i])
                information_sum += information

        if information_sum == 0:
            return 1.0

        standard_error = 1.0 / math.sqrt(information_sum)
        return standard_error

    def should_terminate(self, 
                        responses: List[Dict], 
                        questions: List[Dict], 
                        max_questions: int = None) -> Dict[str, Any]:
        """Determine if assessment should be terminated"""
        max_q = max_questions or self.termination_criteria['max_questions']
        min_q = self.termination_criteria['min_questions']
        se_threshold = self.termination_criteria['standard_error_threshold']

        num_responses = len(responses)
        standard_error = self.calculate_standard_error(responses, questions)

        termination_reasons = []

        if num_responses >= max_q:
            termination_reasons.append('max_questions_reached')

        if num_responses >= min_q and standard_error <= se_threshold:
            termination_reasons.append('sufficient_precision')

        return {
            'should_terminate': len(termination_reasons) > 0,
            'reasons': termination_reasons,
            'num_questions': num_responses,
            'standard_error': standard_error,
            'ability_estimate': self.estimate_ability(responses, questions)
        }

    def generate_adaptive_questions(self, 
                                   user_id: str, 
                                   subject: str, 
                                   topics: List[str], 
                                   config: Dict) -> List[Dict]:
        """Generate questions for adaptive assessment"""
        # This would integrate with the question database and AI generator
        # For now, return a placeholder implementation
        
        total_questions = config.get('total_questions', 20)
        questions = []

        # Generate questions using AI or database
        for i in range(total_questions):
            topic = topics[i % len(topics)] if topics else subject
            
            question_data = {
                'id': f'adaptive_q_{i+1}',
                'question_text': f'Adaptive question {i+1} about {topic}',
                'options': [
                    {'text': 'Option A', 'is_correct': False},
                    {'text': 'Option B', 'is_correct': False},
                    {'text': 'Option C', 'is_correct': True},
                    {'text': 'Option D', 'is_correct': False}
                ],
                'correct_answer': 2,
                'difficulty': 'medium',
                'difficulty_score': 50 + (i * 2),  # Gradually increase difficulty
                'subject': subject,
                'topic': topic,
                'discrimination': 0.5 + (i * 0.01),
                'guessing': 0.25,
                'upper_asymptote': 1.0
            }
            questions.append(question_data)

        return questions

# Global instance
adaptive_algorithm = AdaptiveAlgorithm()
