import unittest
from unittest.mock import patch

from tests.common_code_for_test import is_not_none_string
from moview.modules.question_generator.answer_category_classifier import AnswerCategoryClassifier
from moview.utils.prompt_loader import PromptLoader


class TestAnswerCategoryClassifier(unittest.TestCase):

    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.answer_category_classifier = AnswerCategoryClassifier(self.prompt_loader)

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.answer_category_classifier.prompt))
        print(self.answer_category_classifier.prompt.format())

    @patch(
        'moview.modules.question_generator.answer_category_classifier.AnswerCategoryClassifier'
        '.classify_category_of_answer')
    def test_classify_category_of_answer(self, mock_method):
        # given
        question = "테스트 질문"
        answer = "테스트 답변"
        mock_method.return_value = "classification result"

        # when
        result = self.answer_category_classifier.classify_category_of_answer(question, answer)

        # then
        self.assertIn("classification result", result)
