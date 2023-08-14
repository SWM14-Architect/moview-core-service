import unittest
from unittest.mock import patch

from tests.common_code_for_test import is_not_none_string
from moview.modules.question_generator.answer_sub_category_classifier import AnswerSubCategoryClassifier


class TestAnswerSubCategoryClassifier(unittest.TestCase):

    def setUp(self) -> None:
        self.answer_subcategory_classifier = AnswerSubCategoryClassifier()

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.answer_subcategory_classifier.prompt))
        print(self.answer_subcategory_classifier.prompt.format(job_group="테스트 직군", categories="테스트 카테고리"))

    @patch(
        'moview.modules.question_generator.answer_sub_category_classifier.AnswerSubCategoryClassifier'
        '.classify_sub_category_of_answer')
    def test_classify_sub_category_of_answer(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "테스트 답변"
        category = "테스트 카테고리"
        mock_method.return_value = "classification result"

        # when
        result = self.answer_subcategory_classifier.classify_sub_category_of_answer(job_group, question, answer,
                                                                                    category)

        # then
        self.assertIn("classification result", result)
