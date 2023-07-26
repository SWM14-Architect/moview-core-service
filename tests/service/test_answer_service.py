import unittest
from unittest.mock import patch

from moview.service import IntervieweeDataVO, InterviewActionEnum, IntervieweeInitialInputData
from moview.service.answer_service import AnswerService


class TestAnswerServiceWithMocking(unittest.TestCase):

    def setUp(self) -> None:
        self.answer_service = AnswerService()
        self.initial_input_data = IntervieweeInitialInputData(jop_group="IT", recruit_announcement="공고",
                                                              cover_letter_questions=["질문1", "질문2"],
                                                              cover_letter_answers=["답변1", "답변2"])

    # 초기질문만으로 구성되었을 때, 답변이 부적절한 경우
    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_inappropriate_answer_error_without_followup_question(self, mock_method):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"], initial_interview_analysis="분석",
                               initial_input_data=self.initial_input_data)
        self.assertEqual(len(vo.initial_question_list), 2)
        self.assertEqual(vo.initial_question_index, 0)
        self.assertEqual(len(vo.exclude_question_list), 2)

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
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"], initial_interview_analysis="분석",
                               initial_input_data=self.initial_input_data)
        vo.save_followup_question("꼬리질문1")
        vo.save_followup_question("꼬리질문2")

        self.assertEqual(len(vo.initial_question_list), 2)
        self.assertEqual(vo.initial_question_index, 0)
        self.assertEqual(vo.followup_question_count, 2)
        self.assertEqual(len(vo.exclude_question_list), 4)

        mock_method.return_value = "2"

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group="IT", question="질문",
                                                                                   answer="부적절한 답변", vo=vo)
        # then
        self.assertEqual(vo.initial_question_index, 1)
        self.assertEqual(vo.followup_question_count, 0)
        self.assertEqual(action_enum, InterviewActionEnum.INAPPROPRIATE_ANSWER)
        self.assertEqual(len(vo.exclude_question_list), 4)

    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_resubmission_request_error_without_followup_question(self, mock_method):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"], initial_interview_analysis="분석",
                               initial_input_data=self.initial_input_data)
        self.assertEqual(len(vo.initial_question_list), 2)
        self.assertEqual(vo.initial_question_index, 0)
        self.assertEqual(len(vo.exclude_question_list), 2)

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
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"], initial_interview_analysis="분석",
                               initial_input_data=self.initial_input_data)
        vo.save_followup_question("꼬리질문1")
        vo.save_followup_question("꼬리질문2")

        self.assertEqual(len(vo.initial_question_list), 2)
        self.assertEqual(vo.initial_question_index, 0)
        self.assertEqual(vo.followup_question_count, 2)
        self.assertEqual(len(vo.exclude_question_list), 4)

        mock_method.return_value = "1"

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group="IT", question="질문",
                                                                                   answer="부적절한 답변", vo=vo)
        # then
        self.assertEqual(vo.initial_question_index, 1)
        self.assertEqual(vo.followup_question_count, 0)
        self.assertEqual(action_enum, InterviewActionEnum.DIRECT_REQUEST)
        self.assertEqual(len(vo.exclude_question_list), 4)


"""
아래 테스트는 실제로 gpt call하는 테스트입니다. 그래서 주석처리했습니다.
"""

# class TestAnswerServiceWithoutMocking(unittest.TestCase):
#
#     def setUp(self) -> None:
#         self.answer_service = AnswerService()
#         self.job_group = "IT"
#         self.question = "프로젝트에서 어떤 언어와 프레임워크, 라이브러리를 사용하였나요?"
#         self.answer = "언어는 JAVA, JavaScript를 사용했습니다.프레임워크는 스프링 부트를 사용했습니다."
#
#     # 초기 질문 다 출제하고, 꼬리 질문 하나만 남았을 경우 테스트.
#     def test_end_interview(self):
#         # given
#         vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2", "마지막 질문"],
#                                initial_interview_analysis="분석")
#         vo.initial_question_index = 2
#         vo.save_followup_question("꼬리질문1")
#         vo.save_followup_question("꼬리질문2")
#         vo.save_followup_question(self.question)
#
#         self.assertEqual(len(vo.initial_question_list), 3)
#         self.assertTrue(vo.is_initial_questions_end())
#         self.assertEqual(vo.followup_question_count, 3)
#         self.assertEqual(len(vo.exclude_question_list), 6)
#         self.assertTrue(vo.is_followup_questions_end())
#
#         # when
#         vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group=self.job_group,
#                                                                                    question=self.question,
#                                                                                    answer=self.answer, vo=vo)
#         # then
#         self.assertEqual(vo.initial_question_index, 2)
#         self.assertEqual(vo.followup_question_count, 3)
#         self.assertEqual(action_enum, InterviewActionEnum.END_INTERVIEW)
#         self.assertEqual(len(vo.exclude_question_list), 6)
#         self.assertEqual(len(vo.scores_about_answer), 1)
#
#     # 초기 질문이 마지막이 아니고, 꼬리 질문이 마지막일 경우 테스트.
#     def test_next_initial_question(self):
#         # given
#         vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2", "마지막 질문"],
#                                initial_interview_analysis="분석")
#         vo.initial_question_index = 1  # 2번째 초기 질문 진행 상태
#         vo.save_followup_question("꼬리질문1")
#         vo.save_followup_question("꼬리질문2")
#         vo.save_followup_question(self.question)
#
#         self.assertEqual(len(vo.initial_question_list), 3)
#         self.assertFalse(vo.is_initial_questions_end())
#         self.assertEqual(vo.followup_question_count, 3)
#         self.assertEqual(len(vo.exclude_question_list), 6)
#         self.assertTrue(vo.is_followup_questions_end())
#
#         # when
#         vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group=self.job_group,
#                                                                                    question=self.question,
#                                                                                    answer=self.answer, vo=vo)
#         # then
#         self.assertEqual(vo.initial_question_index, 2)  # 다음 초기 질문 이동
#         self.assertEqual(vo.followup_question_count, 0)
#         self.assertEqual(action_enum, InterviewActionEnum.NEXT_INITIAL_QUESTION)
#         self.assertEqual(len(vo.exclude_question_list), 6)
#         self.assertEqual(len(vo.scores_about_answer), 1)
#
#     def test_get_followup_question(self):
#         # given
#         vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2", "마지막 질문"],
#                                initial_interview_analysis="분석")
#         vo.initial_question_index = 0  # 1번째 초기 질문 진행 상태
#         vo.save_followup_question("꼬리질문1")
#         vo.save_followup_question(self.question)  # 2번째 꼬리질문으로 나온 상태
#
#         self.assertEqual(len(vo.initial_question_list), 3)
#         self.assertFalse(vo.is_initial_questions_end())
#         self.assertEqual(vo.followup_question_count, 2)
#         self.assertEqual(len(vo.exclude_question_list), 5)
#         self.assertFalse(vo.is_followup_questions_end())
#
#         # when
#         vo, action_enum = self.answer_service.determine_next_action_of_interviewer(job_group=self.job_group,
#                                                                                    question=self.question,
#                                                                                    answer=self.answer, vo=vo)
#         # then
#         self.assertEqual(vo.initial_question_index, 0)  # 꼬리질문 아직 안끝냈으므로 그대로.
#         self.assertEqual(vo.followup_question_count, 3)
#         self.assertEqual(action_enum, InterviewActionEnum.CREATED_FOLLOWUP_QUESTION)
#         self.assertEqual(len(vo.exclude_question_list), 6)
#         self.assertEqual(len(vo.scores_about_answer), 1)
#         self.assertTrue(vo.is_followup_questions_end())  # 3번째 꼬리질문이 출제됬으므로 끝났는지 테스트.


if __name__ == '__main__':
    unittest.main()
