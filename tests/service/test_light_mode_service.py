import unittest
from unittest.mock import patch
from moview.repository.input_data.input_data_repository import InputDataRepository
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.config.db.mongo_config import MongoConfig
from moview.utils.prompt_loader import PromptLoader
from moview.service.light_mode_service import LightModeService
from moview.exception.light_question_parse_error import LightQuestionParseError
from moview.modules.light.light_question_giver import LightQuestionGiver


class TestLightModeService(unittest.TestCase):

    def setUp(self) -> None:
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"
        self.prompt_loader = PromptLoader()
        self.question_answer_repository = QuestionAnswerRepository(mongo_config=self.mongo_config)
        self.input_data_repository = InputDataRepository(mongo_config=self.mongo_config)
        self.light_question_giver = LightQuestionGiver(prompt_loader=self.prompt_loader)
        self.light_mode_service = LightModeService(
            input_data_repository=self.input_data_repository,
            question_answer_repository=self.question_answer_repository,
            light_question_giver=self.light_question_giver
        )

        self.interviewee_data = {
            "interviewee_name": "test_user",
            "company_name": "IT회사",
            "job_group": "백엔드",
            "keyword": "데이터베이스, 네트워크",
            "recruit_announcement": None
        }

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.input_data_repository.client.drop_database("test_database")

    @patch("moview.modules.light.light_question_giver.LightQuestionGiver.give_light_questions_by_input_data")
    def test_parse_fail_light_question(self, mock_method):
        # given
        # 예외 강제 발생
        mock_method.side_effect = LightQuestionParseError()

        # when
        result = self.light_mode_service.ask_light_question_to_interviewee(
            interviewee_name=self.interviewee_data["interviewee_name"],
            company_name=self.interviewee_data["company_name"],
            job_group=self.interviewee_data["job_group"],
            keyword=self.interviewee_data["keyword"]
        )

        # then
        self.assertEqual(result, None)

    def test_ask_light_question_to_interviewee_when_keyword_not_exist(self):
        # when
        result = self.light_mode_service.ask_light_question_to_interviewee(
            interviewee_name=self.interviewee_data["interviewee_name"],
            company_name=self.interviewee_data["company_name"],
            job_group=self.interviewee_data["job_group"],
            keyword=None
        )

        # then
        retrieved_document_list = []
        for question_id, question_content in result["question_document_list"]:
            retrieved_document = self.question_answer_repository.find_question_by_object_id(str(question_id))
            retrieved_document_list.append(retrieved_document)

        self.assertEqual(len(retrieved_document_list), 6)

        # 약 3초 소요
        print(retrieved_document_list)

    def test_ask_light_question_to_interviewee_when_keyword_exist(self):
        # when
        result = self.light_mode_service.ask_light_question_to_interviewee(
            interviewee_name=self.interviewee_data["interviewee_name"],
            company_name=self.interviewee_data["company_name"],
            job_group=self.interviewee_data["job_group"],
            keyword=self.interviewee_data["keyword"]
        )

        # then
        retrieved_document_list = []
        for question_id, question_content in result["question_document_list"]:
            retrieved_document = self.question_answer_repository.find_question_by_object_id(str(question_id))
            retrieved_document_list.append(retrieved_document)

        self.assertEqual(len(retrieved_document_list), 6)

        # 4초 정도 소요됨을 확인.
        print(retrieved_document_list)
