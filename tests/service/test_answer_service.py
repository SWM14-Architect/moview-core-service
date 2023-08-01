import unittest
from unittest.mock import patch

from moview.service.interviewee_answer.interviewer_action_enum import InterviewerActionEnum
from moview.service.interviewee_input.interviewee_input_service import IntervieweeInputService, \
    InitialQuestionParseError
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig
from moview.repository.entity.interviewee_data_subdocument import *
from moview.repository.entity.interviewee_data_main_document import IntervieweeDataEntity
from moview.service.interviewee_answer.interviewee_answer_service import IntervieweeAnswerService


class TestAnswerServiceWithMocking(unittest.TestCase):

    def setUp(self) -> None:
        self.answer_service = IntervieweeAnswerService()
        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())
        self.initial_input_data = IntervieweeInitialInputData(interviewee_name="test_user", jop_group="IT",
                                                              recruit_announcement="공고",
                                                              cover_letter_questions=["질문1", "질문2"],
                                                              cover_letter_answers=["답변1", "답변2"])
        self.interviewee_answer_scores = IntervieweeAnswerScores()
        self.interviewee_feedbacks = IntervieweeFeedbacks()

        self.session_id = "testtest1234"

    def tearDown(self):
        self.repository.delete_all_with_id_for_teardown_in_testing(session_id=self.session_id)

    # 초기질문만으로 구성되었을 때, 답변이 부적절한 경우
    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_inappropriate_answer_error_without_followup_question(self, mock_method):
        # given
        interview_questions = InterviewQuestions(initial_question_list=["질문1", "질문2"])
        input_data_analysis_result = InputDataAnalysisResult(input_data_analysis_list=["분석1", "분석 2"])

        entity = IntervieweeDataEntity(session_id=self.session_id, initial_input_data=self.initial_input_data,
                                       input_data_analysis_result=input_data_analysis_result,
                                       interview_questions=interview_questions,
                                       interviewee_answer_scores=self.interviewee_answer_scores,
                                       interviewee_feedbacks=self.interviewee_feedbacks)
        saved_id = self.repository.save(entity)

        self.assertEqual(len(entity.interview_questions.initial_question_list), 2)
        self.assertEqual(entity.interview_questions.initial_question_index, 0)
        self.assertEqual(len(entity.interview_questions.followup_question_list), 0)

        mock_method.return_value = "4"

        # when
        updated_id, action_enum = self.answer_service.determine_next_action_of_interviewer(session_id=saved_id,
                                                                                           question="질문",
                                                                                           answer="부적절한 답변")
        # then
        found_entity = self.repository.find_by_session_id(session_id=updated_id)

        self.assertEqual(found_entity.interview_questions.initial_question_index, 1)
        self.assertEqual(action_enum, InterviewerActionEnum.INAPPROPRIATE_ANSWER)

    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_inappropriate_answer_error_with_followup_question(self, mock_method):
        # given

        interview_questions = InterviewQuestions(initial_question_list=["질문1", "질문2"])
        input_data_analysis_result = InputDataAnalysisResult(input_data_analysis_list=["분석1", "분석 2"])

        entity = IntervieweeDataEntity(session_id=self.session_id, initial_input_data=self.initial_input_data,
                                       input_data_analysis_result=input_data_analysis_result,
                                       interview_questions=interview_questions,
                                       interviewee_answer_scores=self.interviewee_answer_scores,
                                       interviewee_feedbacks=self.interviewee_feedbacks)

        entity.save_followup_question("꼬리질문1")
        entity.save_followup_question("꼬리질문2")

        self.assertEqual(len(entity.interview_questions.initial_question_list), 2)
        self.assertEqual(entity.interview_questions.initial_question_index, 0)
        self.assertEqual(entity.interview_questions.followup_question_count, 2)
        self.assertEqual(len(entity.interview_questions.followup_question_list), 2)

        saved_id = self.repository.save(entity)

        mock_method.return_value = "2"

        # when
        updated_id, action_enum = self.answer_service.determine_next_action_of_interviewer(session_id=saved_id,
                                                                                           question="질문",
                                                                                           answer="부적절한 답변")

        updated_entity = self.repository.find_by_session_id(session_id=updated_id)

        # then
        self.assertEqual(updated_entity.interview_questions.initial_question_index, 1)
        self.assertEqual(updated_entity.interview_questions.followup_question_count, 0)
        self.assertEqual(action_enum, InterviewerActionEnum.INAPPROPRIATE_ANSWER)
        self.assertEqual(len(updated_entity.interview_questions.followup_question_list), 2)

    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_resubmission_request_error_without_followup_question(self, mock_method):
        # given

        interview_questions = InterviewQuestions(initial_question_list=["질문1", "질문2"])
        input_data_analysis_result = InputDataAnalysisResult(input_data_analysis_list=["분석1", "분석 2"])

        entity = IntervieweeDataEntity(session_id=self.session_id, initial_input_data=self.initial_input_data,
                                       input_data_analysis_result=input_data_analysis_result,
                                       interview_questions=interview_questions,
                                       interviewee_answer_scores=self.interviewee_answer_scores,
                                       interviewee_feedbacks=self.interviewee_feedbacks)

        self.assertEqual(len(entity.interview_questions.initial_question_list), 2)
        self.assertEqual(entity.interview_questions.initial_question_index, 0)

        saved_id = self.repository.save(entity)

        mock_method.return_value = "1"

        # when
        updated_id, action_enum = self.answer_service.determine_next_action_of_interviewer(session_id=saved_id,
                                                                                           question="질문",
                                                                                           answer="부적절한 답변")
        updated_entity = self.repository.find_by_session_id(session_id=updated_id)

        # then
        self.assertEqual(updated_entity.interview_questions.initial_question_index, 1)
        self.assertEqual(action_enum, InterviewerActionEnum.DIRECT_REQUEST)
        self.assertEqual(updated_entity.interview_questions.followup_question_count, 0)
        self.assertEqual(len(updated_entity.interview_questions.followup_question_list), 0)

    @patch('moview.modules.question_generator.AnswerFilter.exclude_invalid_answer')
    def test_resubmission_request_error_with_followup_question(self, mock_method):
        # given

        interview_questions = InterviewQuestions(initial_question_list=["질문1", "질문2"])
        input_data_analysis_result = InputDataAnalysisResult(input_data_analysis_list=["분석1", "분석 2"])

        entity = IntervieweeDataEntity(session_id=self.session_id, initial_input_data=self.initial_input_data,
                                       input_data_analysis_result=input_data_analysis_result,
                                       interview_questions=interview_questions,
                                       interviewee_answer_scores=self.interviewee_answer_scores,
                                       interviewee_feedbacks=self.interviewee_feedbacks)

        entity.save_followup_question("꼬리질문1")
        entity.save_followup_question("꼬리질문2")

        self.assertEqual(len(entity.interview_questions.initial_question_list), 2)
        self.assertEqual(entity.interview_questions.initial_question_index, 0)
        self.assertEqual(entity.interview_questions.followup_question_count, 2)
        self.assertEqual(len(entity.interview_questions.followup_question_list), 2)

        mock_method.return_value = "1"

        saved_id = self.repository.save(entity)

        # when
        updated_id, action_enum = self.answer_service.determine_next_action_of_interviewer(session_id=saved_id,
                                                                                           question="질문",
                                                                                           answer="부적절한 답변")
        updated_entity = self.repository.find_by_session_id(session_id=updated_id)

        # then
        self.assertEqual(updated_entity.interview_questions.initial_question_index, 1)
        self.assertEqual(action_enum, InterviewerActionEnum.DIRECT_REQUEST)
        self.assertEqual(updated_entity.interview_questions.followup_question_count, 0)
        self.assertEqual(len(updated_entity.interview_questions.followup_question_list), 2)


"""
아래 테스트는 실제로 gpt call하는 테스트입니다. 
"""


class TestAnswerServiceWithoutMocking(unittest.TestCase):

    def setUp(self) -> None:
        self.answer_service = IntervieweeAnswerService()
        self.initial_input_data = IntervieweeInitialInputData(interviewee_name="test_user", jop_group="IT",
                                                              recruit_announcement="공고",
                                                              cover_letter_questions=["질문1", "질문2"],
                                                              cover_letter_answers=["답변1", "답변2"])
        self.question = "프로젝트에서 어떤 언어와 프레임워크, 라이브러리를 사용하였나요?"
        self.answer = "언어는 JAVA, JavaScript를 사용했습니다.프레임워크는 스프링 부트를 사용했습니다."

    # 초기 질문 다 출제하고, 꼬리 질문 하나만 남았을 경우 테스트.
    def test_end_interview(self):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2", "마지막 질문"],
                               initial_input_data=self.initial_input_data,
                               initial_interview_analysis=["분석1", "분석 2", "분석 3", ])
        vo.interview_questions.initial_question_index = 2
        vo.save_followup_question("꼬리질문1")
        vo.save_followup_question("꼬리질문2")
        vo.save_followup_question(self.question)

        self.assertEqual(len(vo.interview_questions.initial_question_list), 3)
        self.assertTrue(vo.is_initial_questions_end())
        self.assertEqual(vo.interview_questions.followup_question_count, 3)
        self.assertEqual(len(vo.interview_questions.excluded_questions_for_giving_followup_question), 6)
        self.assertTrue(vo.is_followup_questions_end())

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(
            question=self.question,
            answer=self.answer, vo=vo)
        # then
        self.assertEqual(vo.interview_questions.initial_question_index, 2)
        self.assertEqual(vo.interview_questions.followup_question_count, 3)
        self.assertEqual(action_enum, InterviewerActionEnum.END_INTERVIEW)
        self.assertEqual(len(vo.interview_questions.excluded_questions_for_giving_followup_question), 6)
        self.assertEqual(len(vo.answer_score_with_category.categories_ordered_pair_list), 1)

    # 초기 질문이 마지막이 아니고, 꼬리 질문이 마지막일 경우 테스트.
    def test_next_initial_question(self):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2", "마지막 질문"],
                               initial_input_data=self.initial_input_data,
                               initial_interview_analysis=["분석1", "분석 2", "분석 3", ])
        vo.interview_questions.initial_question_index = 1  # 2번째 초기 질문 진행 상태
        vo.save_followup_question("꼬리질문1")
        vo.save_followup_question("꼬리질문2")
        vo.save_followup_question(self.question)

        self.assertEqual(len(vo.interview_questions.initial_question_list), 3)
        self.assertFalse(vo.is_initial_questions_end())
        self.assertEqual(vo.interview_questions.followup_question_count, 3)
        self.assertEqual(len(vo.interview_questions.excluded_questions_for_giving_followup_question), 6)
        self.assertTrue(vo.is_followup_questions_end())

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(
            question=self.question,
            answer=self.answer, vo=vo)
        # then
        self.assertEqual(vo.interview_questions.initial_question_index, 2)  # 다음 초기 질문 이동
        self.assertEqual(vo.interview_questions.followup_question_count, 0)
        self.assertEqual(action_enum, InterviewerActionEnum.NEXT_INITIAL_QUESTION)
        self.assertEqual(len(vo.interview_questions.excluded_questions_for_giving_followup_question), 6)
        self.assertEqual(len(vo.answer_score_with_category.categories_ordered_pair_list), 1)

    def test_get_followup_question(self):
        # given
        vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2", "마지막 질문"],
                               initial_input_data=self.initial_input_data,
                               initial_interview_analysis=["분석1", "분석 2", "분석 3", ])
        vo.interview_questions.initial_question_index = 0  # 1번째 초기 질문 진행 상태
        vo.save_followup_question("꼬리질문1")
        vo.save_followup_question(self.question)  # 2번째 꼬리질문으로 나온 상태

        self.assertEqual(len(vo.interview_questions.initial_question_list), 3)
        self.assertFalse(vo.is_initial_questions_end())
        self.assertEqual(vo.interview_questions.followup_question_count, 2)
        self.assertEqual(len(vo.interview_questions.excluded_questions_for_giving_followup_question), 5)
        self.assertFalse(vo.is_followup_questions_end())

        # when
        vo, action_enum = self.answer_service.determine_next_action_of_interviewer(
            question=self.question,
            answer=self.answer, vo=vo)
        # then
        self.assertEqual(vo.interview_questions.initial_question_index, 0)  # 꼬리질문 아직 안끝냈으므로 그대로.
        self.assertEqual(vo.interview_questions.followup_question_count, 3)
        self.assertEqual(action_enum, InterviewerActionEnum.CREATED_FOLLOWUP_QUESTION)
        self.assertEqual(len(vo.interview_questions.excluded_questions_for_giving_followup_question), 6)
        self.assertEqual(len(vo.answer_score_with_category.categories_ordered_pair_list), 1)
        self.assertTrue(vo.is_followup_questions_end())  # 3번째 꼬리질문이 출제됬으므로 끝났는지 테스트.


if __name__ == '__main__':
    unittest.main()
