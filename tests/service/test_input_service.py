import asynctest
from asynctest.mock import patch

from moview.modules.input import InputAnalyzer
from moview.modules.input.initial_question_giver import InitialQuestionGiver
from moview.exception.initial_question_parse_error import InitialQuestionParseError
from moview.service.input_data_service import InputDataService
from moview.repository.input_data.input_data_repository import InputDataRepository
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.config.db.mongo_config import MongoConfig
from moview.utils.prompt_loader import PromptLoader


class TestInputService(asynctest.TestCase):
    def setUp(self):
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"
        self.prompt_loader = PromptLoader()
        self.question_answer_repositroy = QuestionAnswerRepository(mongo_config=self.mongo_config)
        self.input_data_repository = InputDataRepository(mongo_config=self.mongo_config)
        self.initial_input_analyzer = InputAnalyzer(prompt_loader=self.prompt_loader)
        self.initial_question_giver = InitialQuestionGiver(prompt_loader=self.prompt_loader)
        self.input_data_service = InputDataService(
            question_answer_repository=self.question_answer_repositroy,
            input_data_repository=self.input_data_repository,
            initial_input_analyzer=self.initial_input_analyzer,
            initial_question_giver=self.initial_question_giver
        )

        self.interviewee_data = {
            "interviewee_name": "test_user",
            "company_name": "IT회사",
            "job_group": "IT",
            "recruit_announcement": "창의력이 뛰어난 프로그래밍 전문가 모집합니다"
        }

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.input_data_repository.client.drop_database("test_database")

    async def test_cover_letter_questions_and_answers_length_are_not_not_equal(self):
        # given
        cover_letter_questions = ["질문1", "질문2"]
        cover_letter_answers = ["답변1"]

        # when
        with self.assertRaises(ValueError):
            await self.input_data_service.ask_initial_question_to_interviewee(
                **self.interviewee_data,
                cover_letter_questions=cover_letter_questions,
                cover_letter_answers=cover_letter_answers
            )

    @patch('moview.modules.input.initial_question_giver.InitialQuestionGiver.give_initial_questions')
    @patch('moview.modules.input.initial_question_giver.InitialQuestionGiver.give_initial_questions_by_input_data')
    async def test_parse_fail_initial_question(self, mock_method2, mock_method1):
        # given
        # 예외 강제 발생
        mock_method1.side_effect = InitialQuestionParseError()
        mock_method2.side_effect = InitialQuestionParseError()

        # when
        with self.assertRaises(InitialQuestionParseError):
            await self.input_data_service.ask_initial_question_to_interviewee(
                **self.interviewee_data,
                cover_letter_questions=["당신의 창의력을 어떻게 발휘해 왔습니까?"],
                cover_letter_answers=["여러 언어를 이용한 프로그램 개발을 통해 독특한 해결책을 제시해 왔습니다."]
            )

    @patch('moview.modules.input.input_analyzer.InputAnalyzer.analyze_initial_input')
    async def test_ask_initial_question_to_interviewee_without_analyze(self, mock_method):
        # given
        mock_method.return_value = "평가"
        
        # when
        result = await self.input_data_service.ask_initial_question_to_interviewee(
            **self.interviewee_data,
            cover_letter_questions=["당신의 창의력을 어떻게 발휘해 왔습니까?"],
            cover_letter_answers=["여러 언어를 이용한 프로그램 개발을 통해 독특한 해결책을 제시해 왔습니다."]
        )

        # then
        retrieved_document_list = []
        for question_id, question_content in result["question_document_list"]:
            retrieved_document = self.question_answer_repositroy.find_question_by_object_id(str(question_id))
            retrieved_document_list.append(retrieved_document)

        self.assertEqual(len(retrieved_document_list), 6)

    async def test_ask_initial_question_to_interviewee(self):
        # when
        result = await self.input_data_service.ask_initial_question_to_interviewee(
            **self.interviewee_data,
            cover_letter_questions=[
                "당신의 창의력을 어떻게 발휘해 왔습니까?",
                "지원하게 된 이유를 설명해주세요."
            ],
            cover_letter_answers=[
                "여러 언어를 이용한 프로그램 개발을 통해 독특한 해결책을 제시해 왔습니다.",
                "저의 창의력을 활용하여 사회에 기여하고 싶어서 입니다."
            ]
        )

        # then
        retrieved_document_list = []
        for question_id, question_content in result["question_document_list"]:
            retrieved_document = self.question_answer_repositroy.find_question_by_object_id(str(question_id))
            retrieved_document_list.append(retrieved_document)

        self.assertEqual(len(retrieved_document_list), 6)
