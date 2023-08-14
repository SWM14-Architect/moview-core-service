import unittest

from moview.repository.entity.interviewee_data_subdocument import *
from moview.repository.entity.interviewee_data_main_document import IntervieweeDataEntity
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig
from moview.service.interviewee_feedback.interviewee_feedback_service import IntervieweeFeedbackService


class TestIntervieweeFeedbackService(unittest.TestCase):

    def setUp(self) -> None:
        self.feedback_service = IntervieweeFeedbackService()
        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())

        self.initial_input_data = IntervieweeInitialInputData(interviewee_name="test_user", jop_group="IT",
                                                              recruit_announcement="공고",
                                                              cover_letter_questions=["질문1", "질문2"],
                                                              cover_letter_answers=["답변1", "답변2"])
        self.interviewee_answer_evaluations = IntervieweeAnswerEvaluations()
        self.interviewee_feedbacks = IntervieweeFeedbacks()
        self.session_id = "testtest1234"

    def tearDown(self):
        self.repository.delete_all_with_id_for_teardown_in_testing(session_id=self.session_id)

    def test_save_feedback_of_interviewee(self):
        # given
        entity = IntervieweeDataEntity(session_id=self.session_id, initial_input_data=self.initial_input_data,
                                       input_data_analysis_result=InputDataAnalysisResult(
                                           input_data_analysis_list=["분석1", "분석 2"]),
                                       interview_questions=InterviewQuestions(
                                           initial_question_list=["질문1", "질문2"]),
                                       interviewee_answer_evaluations=self.interviewee_answer_evaluations,
                                       interviewee_feedbacks=self.interviewee_feedbacks)

        saved_id = self.repository.save(interviewee_data_entity=entity)

        # when
        feedback_list = ["피드백1", "피드백2", "피드백3"]
        updated_id = self.feedback_service.save_feedback_of_interviewee(session_id=saved_id, feedback_list=feedback_list)

        # then
        found_entity = self.repository.find_by_session_id(session_id=updated_id)

        self.assertEqual(len(found_entity.interviewee_feedbacks.feedback_list), 3)
