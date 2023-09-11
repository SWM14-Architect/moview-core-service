import unittest
from unittest.mock import patch
from moview.service.answer_service import AnswerService
from moview.config.db.mongo_config import MongoConfig
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.repository.interview_repository import InterviewRepository
from moview.modules.question_generator import FollowUpQuestionGiver
from moview.utils.prompt_loader import PromptLoader
from moview.domain.entity.interview_session_document import InterviewSession
from moview.domain.entity.question_answer.question import Question

PATCH_PATH = "moview.service.answer_service.AnswerService.need_to_give_followup_question"


class TestAnswerService(unittest.TestCase):

    def setUp(self):
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"

        self.prompt_loader = PromptLoader()
        self.giver = FollowUpQuestionGiver(self.prompt_loader)

        self.interview_repository = InterviewRepository(self.mongo_config)
        self.question_answer_repository = QuestionAnswerRepository(self.mongo_config)

        self.user_id = "1"
        self.interview = InterviewSession(user_id=self.user_id)
        self.interview_id = self.interview_repository.save_interview(self.interview).inserted_id

        self.initial_question = Question(content="질문 내용", feedback_score=0, question_id=None)
        self.initial_question_id = self.question_answer_repository.save_question(self.initial_question).inserted_id

        self.answer_service = AnswerService(self.interview_repository, self.question_answer_repository, self.giver)

        self.question_content = "이 회사에서 어떻게 성과를 낼 건지 말씀해주세요."
        self.answer_content = "탁월한 개발자로서 이 회사의 핵심 인재가 되겠습니다. 그리고 신입 개발자들의 온보딩을 도움으로써 회사의 효율성을 높이는 시니어 개발자가 될 것입니다."

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.interview_repository.client.drop_database("test_database")
        self.question_answer_repository.client.drop_database("test_database")

    def test_singleton(self):
        # when
        answer_service1 = AnswerService(self.interview_repository, self.question_answer_repository, self.giver)
        answer_service2 = AnswerService(self.interview_repository, self.question_answer_repository, self.giver)
        # then
        self.assertEqual(answer_service1, answer_service2)

    @patch(PATCH_PATH)
    def test_no_need_followup_question(self, mock_method):
        # given
        mock_method.return_value = False

        # when
        content, saved_id = self.answer_service.answer(user_id=self.user_id,
                                                       interview_id=self.interview_id,
                                                       question_id=str(self.initial_question_id),
                                                       question_content=self.question_content,
                                                       answer_content=self.answer_content)

        interview = self.interview_repository.find_interview_by_object_id(self.user_id, self.interview_id)

        # then
        self.assertTrue(content is None)
        self.assertTrue(saved_id is None)
        self.assertTrue(len(interview['previous_question_content']) == 1)
        print("\ncontent : ", content)

    @patch(PATCH_PATH)
    def test_need_followup_question(self, mock_method):
        # given
        mock_method.return_value = True
        # when
        content, saved_id = self.answer_service.answer(user_id=self.user_id,
                                                       interview_id=self.interview_id,
                                                       question_id=str(self.initial_question_id),
                                                       question_content=self.question_content,
                                                       answer_content=self.answer_content)

        interview = self.interview_repository.find_interview_by_object_id(self.user_id, self.interview_id)

        # then
        self.assertTrue(content is not None)
        question_id = self.question_answer_repository.find_question_by_object_id(saved_id)
        self.assertEqual(str(question_id.get("_id")), str(saved_id))
        self.assertTrue(len(interview['previous_question_content']) == 1)
        print("\ncontent : ", content)

    @patch(PATCH_PATH)
    def test_followup_of_followup(self, mock_method):
        # given
        mock_method.return_value = True

        content1, saved_id1 = self.answer_service.answer(user_id=self.user_id,
                                                         interview_id=self.interview_id,
                                                         question_id=str(self.initial_question_id),
                                                         question_content=self.question_content,
                                                         answer_content=self.answer_content)

        # when
        content2, saved_id2 = self.answer_service.answer(user_id=self.user_id,
                                                         interview_id=self.interview_id,
                                                         question_id=str(saved_id1),
                                                         question_content=content1,
                                                         answer_content="신입 사원이 온보딩을 쉽게 할 수 있도록 코드 베이스와 문서를 잘 정리해놓을 것입니다.")

        interview = self.interview_repository.find_interview_by_object_id(self.user_id, self.interview_id)

        # then
        self.assertTrue(content2 is not None)
        question_id = self.question_answer_repository.find_question_by_object_id(saved_id2)
        self.assertEqual(str(question_id.get("_id")), str(saved_id2))
        self.assertTrue(len(interview['previous_question_content']) == 2)
        print("\ncontent : ", content1)
        print("\ncontent : ", content2)
