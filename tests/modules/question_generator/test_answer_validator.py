import unittest
from unittest.mock import patch

from tests.common_code_for_test import is_not_none_string
from moview.modules.question_generator.answer_validator import AnswerValidator


class TestAnswerValidator(unittest.TestCase):

    def setUp(self) -> None:
        self.answer_filter = AnswerValidator()

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.answer_filter.prompt))
        print(self.answer_filter.prompt.format(job_group="테스트 직군"))

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_direct_request(self, mock_method):
        # given
        question = "테스트 질문"
        answer = "질문 재요청"
        mock_method.return_value = "1"

        # when
        result = self.answer_filter.exclude_invalid_answer(question, answer)

        # then
        self.assertIn("1", result)

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_uncertain_response(self, mock_method):
        # given
        question = "테스트 질문"
        answer = "불확실한 답변"
        mock_method.return_value = "2"

        # when
        result = self.answer_filter.exclude_invalid_answer(question, answer)

        # then
        self.assertIn("2", result)

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_minimal_response(self, mock_method):
        # given
        question = "테스트 질문"
        answer = "불충분한 답변"
        mock_method.return_value = "3"

        # when
        result = self.answer_filter.exclude_invalid_answer(question, answer)

        # then
        self.assertIn("3", result)

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_off_topic_response(self, mock_method):
        # given
        question = "테스트 질문"
        answer = "헛소리"
        mock_method.return_value = "4"

        # when
        result = self.answer_filter.exclude_invalid_answer(question, answer)

        # then
        self.assertIn("4", result)

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_good_answer(self, mock_method):
        # given
        question = "테스트 질문"
        answer = "테스트 답변"
        mock_method.return_value = "5"

        # when
        result = self.answer_filter.exclude_invalid_answer(question, answer)

        # then
        self.assertIn("5", result)
