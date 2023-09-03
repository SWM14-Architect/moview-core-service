import unittest
from unittest.mock import patch
from moview.service.answer_service import AnswerService


class TestAnswerService(unittest.TestCase):

    def setUp(self):
        self.answer_service = AnswerService()

    def test_print_probability_of_followup_question(self):
        base_probability_of_question = 0.6  # 기본 확률

        num_questions_asked = 0

        for i in range(50):
            # 출제된 질문이 많아질수록 확률이 감소
            prob = base_probability_of_question / (1 + 0.1 * num_questions_asked)
            print(f"Iteration {i + 1}, Probability: {prob:.4f}")
            num_questions_asked += 1
