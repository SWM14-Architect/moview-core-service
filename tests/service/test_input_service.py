import unittest
from unittest.mock import patch

from moview.service.interviewee_input.interviewee_input_service import IntervieweeInputService, \
    InitialQuestionParseError
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig


class TestInputService(unittest.TestCase):
    def setUp(self):
        self.input_service = IntervieweeInputService()
        self.recruit_announcement = "창의력이 뛰어난 프로그래밍 전문가 모집합니다"
        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())

    def tearDown(self):
        self.repository.delete_all_with_id_for_teardown_in_testing(session_id="testtest1234")

    def test_cover_letter_questions_and_answers_length_are_not_not_equal(self):
        # given
        cover_letter_questions = ["질문1", "질문2"]
        cover_letter_answers = ["답변1"]

        # when
        with self.assertRaises(ValueError):
            self.input_service.ask_initial_question_to_interviewee(session_id="testtest1234",
                                                                   interviewee_name="test_user", job_group="IT",
                                                                   recruit_announcement="공고",
                                                                   cover_letter_questions=cover_letter_questions,
                                                                   cover_letter_answers=cover_letter_answers)

    @patch('moview.modules.input.initial_question_giver.InitialQuestionGiver.give_initial_questions')
    def test_parse_fail_initial_question(self, mock_method):
        # given
        # 예외 강제 발생
        mock_method.side_effect = InitialQuestionParseError()

        # when
        saved_id = self.input_service.ask_initial_question_to_interviewee(session_id="testtest1234",
                                                                          interviewee_name="test_user", job_group="IT",
                                                                          recruit_announcement=self.recruit_announcement,
                                                                          cover_letter_questions=[
                                                                              "당신의 창의력을 어떻게 발휘해 왔습니까?"],
                                                                          cover_letter_answers=[
                                                                              "여러 언어를 이용한 프로그램 개발을 통해 독특한 해결책을 제시해 왔습니다."])
        # then
        loaded_entity = self.repository.find_by_session_id(saved_id)
        self.assertEqual(loaded_entity.interview_questions.initial_question_list, [[], []])

    def test_ask_initial_question_to_interviewee_with_one_cover_letter(self):
        # when
        saved_id = self.input_service.ask_initial_question_to_interviewee(session_id="testtest1234",
                                                                          interviewee_name="test_user", job_group="IT",
                                                                          recruit_announcement=self.recruit_announcement,
                                                                          cover_letter_questions=[
                                                                              "당신의 창의력을 어떻게 발휘해 왔습니까?"],
                                                                          cover_letter_answers=[
                                                                              "여러 언어를 이용한 프로그램 개발을 통해 독특한 해결책을 제시해 왔습니다."])

        # then
        loaded_entity = self.repository.find_by_session_id(saved_id)
        self.assertEqual(len(loaded_entity.input_data_analysis_result.input_data_analysis_list), 1)
        self.assertEqual(len(loaded_entity.interview_questions.initial_question_list), 2)

    def test_ask_initial_question_to_interviewee_with_two_cover_letter(self):
        # when
        saved_id = self.input_service.ask_initial_question_to_interviewee(session_id="testtest1234",
                                                                          interviewee_name="test_user", job_group="IT",
                                                                          recruit_announcement=self.recruit_announcement,
                                                                          cover_letter_questions=[
                                                                              "당신의 창의력을 어떻게 발휘해 왔습니까?",
                                                                              "가장 도전적인 프로젝트 경험은 무엇인가요?"],
                                                                          cover_letter_answers=[
                                                                              "여러 언어를 이용한 프로그램 개발을 통해 독특한 해결책을 제시해 왔습니다.",
                                                                              "빅데이터 분석을 위한 알고리즘 개발 프로젝트에서 주도적인 역할을 수행하였습니다."])

        # then
        loaded_entity = self.repository.find_by_session_id(saved_id)
        self.assertEqual(len(loaded_entity.input_data_analysis_result.input_data_analysis_list), 2)
        self.assertEqual(len(loaded_entity.interview_questions.initial_question_list), 4)

    def test_ask_initial_question_to_interviewee_with_three_cover_letter(self):
        # when
        saved_id = self.input_service.ask_initial_question_to_interviewee(session_id="testtest1234",
                                                                          interviewee_name="test_user", job_group="IT",
                                                                          recruit_announcement=self.recruit_announcement,
                                                                          cover_letter_questions=[
                                                                              "당신의 창의력을 어떻게 발휘해 왔습니까?",
                                                                              "가장 도전적인 프로젝트 경험은 무엇인가요?",
                                                                              "당신의 장점은 무엇인가요?"],
                                                                          cover_letter_answers=[
                                                                              "여러 언어를 이용한 프로그램 개발을 통해 독특한 해결책을 제시해 왔습니다.",
                                                                              "빅데이터 분석을 위한 알고리즘 개발 프로젝트에서 주도적인 역할을 수행하였습니다.",
                                                                              "빠른 학습력과 뛰어난 커뮤니케이션 능력을 갖추고 있습니다."])

        # then
        loaded_entity = self.repository.find_by_session_id(saved_id)
        self.assertEqual(len(loaded_entity.input_data_analysis_result.input_data_analysis_list), 3)
        self.assertEqual(len(loaded_entity.interview_questions.initial_question_list), 6)
