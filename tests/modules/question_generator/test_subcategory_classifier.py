import unittest
from unittest.mock import patch

from moview.modules.question_generator.answer_subcategory_classifier import AnswerSubCategoryClassifier


class TestAnswerSubCategoryClassifier(unittest.TestCase):
    def setUp(self) -> None:
        self.answer_subcategory_classifier = AnswerSubCategoryClassifier()

    @patch(
        'moview.modules.question_generator.answer_subcategory_classifier.AnswerSubCategoryClassifier'
        '.classify_sub_category_of_answer')
    def test_classify_sub_category_of_answer(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "테스트 답변"
        mock_method.return_value = "classification result"

        # when
        result = self.answer_subcategory_classifier.classify_sub_category_of_answer(job_group, question, answer)

        # then
        self.assertIn("classification result", result)
