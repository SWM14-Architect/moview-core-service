import unittest

from moview.repository.entity.interviewee_data_subdocument import *
from moview.repository.entity.interviewee_data_main_document import IntervieweeDataEntity
from moview.service.interviewee_evaluation.interviewee_answer_evaluation_service import InterviewAnswerEvaluationService
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig


class TestIntervieweeAnswerEvaluationService(unittest.TestCase):

    def setUp(self) -> None:
        self.evaluation_service = InterviewAnswerEvaluationService()
        self.initial_input_data = IntervieweeInitialInputData(interviewee_name="test_user", jop_group="IT",
                                                              recruit_announcement="공고",
                                                              cover_letter_questions=["질문1", "질문2"],
                                                              cover_letter_answers=["답변1", "답변2"])
        self.interviewee_answer_evaluations = IntervieweeAnswerEvaluations()

        self.interviewee_feedbacks = IntervieweeFeedbacks()

        self.session_id = "testtest1234"

        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())

    def tearDown(self):
        self.repository.delete_all_with_id_for_teardown_in_testing(session_id=self.session_id)

    def test_evaluate_one_answer_of_interviewee(self):
        # given
        entity = IntervieweeDataEntity(session_id=self.session_id, initial_input_data=self.initial_input_data,
                                       input_data_analysis_result=InputDataAnalysisResult(
                                           input_data_analysis_list=["분석1", "분석 2"]),
                                       interview_questions=InterviewQuestions(
                                           initial_question_list=["질문1", "질문2"]),
                                       interviewee_answer_evaluations=self.interviewee_answer_evaluations,
                                       interviewee_feedbacks=self.interviewee_feedbacks)

        entity.save_category_in_interviewee_answer_evaluations(question="프로젝트에서 어떤 언어와 프레임워크, 라이브러리를 사용하였나요?",
                                                               answer="언어는 JAVA, JavaScript를 사용했습니다.프레임워크는 스프링 부트를 사용했습니다.",
                                                               category_and_sub_category="Technical Job-related Questions, specifically the subcategory of Technical Details.")

        saved_id = self.repository.save(interviewee_data_entity=entity)

        # when
        updated_id = self.evaluation_service.evaluate_answers_of_interviewee(session_id=saved_id)

        # then
        found_entity = self.repository.find_by_session_id(session_id=updated_id)

        self.assertEqual(len(found_entity.interviewee_answer_evaluations.score_of_answer_list), 1)
        self.assertEqual(len(found_entity.interviewee_answer_evaluations.analysis_of_answer_list), 1)
        print("\nPRINT\n")
        print("\n", found_entity.interviewee_answer_evaluations.score_of_answer_list)
        print("\n", found_entity.interviewee_answer_evaluations.analysis_of_answer_list)

    def test_evaluate_answers_of_interviewee(self):
        # given
        ANSWER_COUNT = 2

        entity = IntervieweeDataEntity(session_id=self.session_id, initial_input_data=self.initial_input_data,
                                       input_data_analysis_result=InputDataAnalysisResult(
                                           input_data_analysis_list=["분석1", "분석 2"]),
                                       interview_questions=InterviewQuestions(
                                           initial_question_list=["질문1", "질문2"]),
                                       interviewee_answer_evaluations=self.interviewee_answer_evaluations,
                                       interviewee_feedbacks=self.interviewee_feedbacks)

        for _ in range(ANSWER_COUNT):
            entity.save_category_in_interviewee_answer_evaluations(question="프로젝트에서 어떤 언어와 프레임워크, 라이브러리를 사용하였나요?",
                                                                   answer="언어는 JAVA, JavaScript를 사용했습니다.프레임워크는 스프링 부트를 사용했습니다.",
                                                                   category_and_sub_category="Technical Job-related Questions, specifically the subcategory of Technical Details.")
        saved_id = self.repository.save(interviewee_data_entity=entity)

        # when
        updated_id = self.evaluation_service.evaluate_answers_of_interviewee(session_id=saved_id)

        # then
        found_entity = self.repository.find_by_session_id(session_id=updated_id)
        self.assertEqual(len(found_entity.interviewee_answer_evaluations.score_of_answer_list), ANSWER_COUNT)
        self.assertEqual(len(found_entity.interviewee_answer_evaluations.analysis_of_answer_list), ANSWER_COUNT)

        print("\nPRINT\n")
        for i in range(len(found_entity.interviewee_answer_evaluations.score_of_answer_list)):
            print("\n", found_entity.interviewee_answer_evaluations.score_of_answer_list[i])
        for i in range(len(found_entity.interviewee_answer_evaluations.analysis_of_answer_list)):
            print("\n", found_entity.interviewee_answer_evaluations.analysis_of_answer_list[i])
        """
        출력 형태
        (첫 번째 경우)
        - Technical Details
            - Technical Knowledge (0-100 points): 80#
            - Technical Depth (0-100 points): 70#
            - Practical Application (0-100 points): 90#
        
        (두 번째 경우) 
        - Technical Details

            - Technical Knowledge: 85#
            - Technical Depth: 70#
            - Practical Application: 90#   
        
        (세 번째 경우) 
        - Technical Details

            - Technical Knowledge (85#)
            - Technical Depth (80#)
            - Practical Application (90#)
        
        (네 번째 경우)
        Evaluation:
        
        - Technical Knowledge (0-100 points): 80#
        - The candidate accurately identifies the languages and frameworks used in their project.
        - Technical Depth (0-100 points): 70#
        
        Overall Score: 80
        
        (다섯 번째 경우)
         Technical Job-related Questions - Technical Details:
        - Technical Knowledge: 80#
        - Technical Depth: 70#     
        - Practical Application: 90#
        """
