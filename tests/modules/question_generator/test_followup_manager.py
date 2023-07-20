import unittest
from unittest.mock import MagicMock, patch

from moview.modules.question_generator.followup_question_manager import FollowUpQuestionManager, \
    InappropriateAnswerError, \
    ResubmissionRequestError


class TestFollowUpQuestionManager(unittest.TestCase):
    def setUp(self):
        self.manager = FollowUpQuestionManager()

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.check_answer_appropriate')
    def test_manage_followup_question_resubmission_error(self, mock_method):
        mock_method.return_value = "1"
        with self.assertRaises(ResubmissionRequestError):
            self.manager.manage_followup_question("job_group", "question", "answer")

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.check_answer_appropriate')
    def test_manage_followup_question_inappropriate_error(self, mock_find_first_number):
        mock_find_first_number.return_value = "2"
        with self.assertRaises(InappropriateAnswerError):
            self.manager.manage_followup_question("job_group", "question", "answer")

    @patch('moview.modules.question_generator.answer_filter.AnswerFilter.check_answer_appropriate')
    def test_manage_followup_question(self, mock_method):
        self.manager.major.classify_category_of_answer = MagicMock(return_value="major_category")
        self.manager.sub.classify_sub_category_of_answer = MagicMock(return_value="sub_category")
        self.manager.giver.give_followup_question = MagicMock(return_value="followup_question")

        # find_first_number의 결과를 mock
        mock_method.return_value = "5"

        # 테스트 실행
        result = self.manager.manage_followup_question("job_group", "question", "answer")

        # 결과 확인
        self.assertEqual(result, "followup_question")


if __name__ == '__main__':
    unittest.main()
