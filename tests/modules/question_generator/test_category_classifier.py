import unittest
from unittest.mock import patch

from moview.modules.question_generator.answer_category_classifier import AnswerCategoryClassifier


def is_not_none_string(s):
    return s is not None and isinstance(s, str)


class TestAnswerCategoryClassifier(unittest.TestCase):
    def setUp(self) -> None:
        self.answer_category_classifier = AnswerCategoryClassifier()

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.answer_category_classifier.prompt))
        print(self.answer_category_classifier.prompt.format(job_group="테스트 직군"))

    @patch(
        'moview.modules.question_generator.answer_category_classifier.AnswerCategoryClassifier'
        '.classify_category_of_answer')
    def test_classify_category_of_answer(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "테스트 답변"
        mock_method.return_value = "classification result"

        # when
        result = self.answer_category_classifier.classify_category_of_answer(job_group, question, answer)

        # then
        self.assertIn("classification result", result)
