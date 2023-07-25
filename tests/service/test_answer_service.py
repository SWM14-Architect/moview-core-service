import unittest
from unittest.mock import Mock, patch

from moview.service import IntervieweeDataVO, InterviewActionEnum
from moview.service.answer_service import AnswerService, InappropriateAnswerError, ResubmissionRequestError


class TestAnswerService(unittest.TestCase):

    def setUp(self) -> None:
        self.answer_service = AnswerService()

    # 초기질문만으로 구성되었을 때, 답변이 부적절한 경우
    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_inappropriate_answer_error_without_followup_question(self, mock_method):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"], initial_interview_analysis="분석")
        self.assertEqual(len(vo.initial_question_list), 2)
        self.assertEqual(vo.initial_question_index, 0)

        mock_method.return_value = "4"

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group="IT", question="질문",
                                                                                   answer="부적절한 답변", vo=vo)
        # then
        self.assertEqual(vo.initial_question_index, 1)
        self.assertEqual(action_enum, InterviewActionEnum.INAPPROPRIATE_ANSWER)

    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_inappropriate_answer_error_with_followup_question(self, mock_method):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"], initial_interview_analysis="분석")
        vo.save_followup_question("꼬리질문1")
        vo.save_followup_question("꼬리질문2")

        self.assertEqual(len(vo.initial_question_list), 2)
        self.assertEqual(vo.initial_question_index, 0)
        self.assertEqual(vo.followup_question_count, 2)
        self.assertEqual(len(vo.previous_question_list), 2)

        mock_method.return_value = "2"

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group="IT", question="질문",
                                                                                   answer="부적절한 답변", vo=vo)
        # then
        self.assertEqual(vo.initial_question_index, 1)
        self.assertEqual(vo.followup_question_count, 0)
        self.assertEqual(action_enum, InterviewActionEnum.INAPPROPRIATE_ANSWER)
        self.assertEqual(len(vo.previous_question_list), 2)

    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_resubmission_request_error_without_followup_question(self, mock_method):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"], initial_interview_analysis="분석")
        self.assertEqual(len(vo.initial_question_list), 2)
        self.assertEqual(vo.initial_question_index, 0)

        mock_method.return_value = "1"

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group="IT", question="질문",
                                                                                   answer="부적절한 답변", vo=vo)
        # then
        self.assertEqual(vo.initial_question_index, 1)
        self.assertEqual(action_enum, InterviewActionEnum.DIRECT_REQUEST)

    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_resubmission_request_error_with_followup_question(self, mock_method):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"], initial_interview_analysis="분석")
        vo.save_followup_question("꼬리질문1")
        vo.save_followup_question("꼬리질문2")

        self.assertEqual(len(vo.initial_question_list), 2)
        self.assertEqual(vo.initial_question_index, 0)
        self.assertEqual(vo.followup_question_count, 2)
        self.assertEqual(len(vo.previous_question_list), 2)

        mock_method.return_value = "1"

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group="IT", question="질문",
                                                                                   answer="부적절한 답변", vo=vo)
        # then
        self.assertEqual(vo.initial_question_index, 1)
        self.assertEqual(vo.followup_question_count, 0)
        self.assertEqual(action_enum, InterviewActionEnum.DIRECT_REQUEST)
        self.assertEqual(len(vo.previous_question_list), 2)
