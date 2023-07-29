import unittest
from unittest.mock import patch

from moview.modules.question_generator.answer_filter import AnswerFilter


def is_not_none_string(s):
    return s is not None and isinstance(s, str)


class TestAnswerFilter(unittest.TestCase):

    def setUp(self) -> None:
        self.answer_filter = AnswerFilter()

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.answer_filter.prompt))
        print(self.answer_filter.prompt.format(job_group="테스트 직군"))

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_direct_request(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "질문 재요청"
        mock_method.return_value = "1"

        # when
        result = self.answer_filter.exclude_invalid_answer(job_group, question, answer)

        # then
        self.assertIn("1", result)

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_uncertain_response(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "불확실한 답변"
        mock_method.return_value = "2"

        # when
        result = self.answer_filter.exclude_invalid_answer(job_group, question, answer)

        # then
        self.assertIn("2", result)

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_minimal_response(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "불충분한 답변"
        mock_method.return_value = "3"

        # when
        result = self.answer_filter.exclude_invalid_answer(job_group, question, answer)

        # then
        self.assertIn("3", result)

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_off_topic_response(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "헛소리"
        mock_method.return_value = "4"

        # when
        result = self.answer_filter.exclude_invalid_answer(job_group, question, answer)

        # then
        self.assertIn("4", result)

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.exclude_invalid_answer')
    def test_check_answer_appropriate_if_good_answer(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "테스트 답변"
        mock_method.return_value = "5"

        # when
        result = self.answer_filter.exclude_invalid_answer(job_group, question, answer)

        # then
        self.assertIn("5", result)
