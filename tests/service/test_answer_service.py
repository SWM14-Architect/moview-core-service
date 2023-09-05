import unittest
from unittest.mock import patch
from moview.service.answer_service import AnswerService
from moview.config.db.mongo_config import MongoConfig
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.repository.interview_repository import InterviewRepository
from moview.modules.question_generator import AnswerFilter, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver
from moview.utils.prompt_loader import PromptLoader
from moview.domain.entity.interview_session_document import InterviewSession
from moview.domain.entity.question_answer.question import Question
from bson import ObjectId


class TestAnswerService(unittest.TestCase):

    def setUp(self):
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"

        self.prompt_loader = PromptLoader()

        self.answer_filter = AnswerFilter(self.prompt_loader)
        self.major_classifier = AnswerCategoryClassifier(self.prompt_loader)
        self.sub_classifier = AnswerSubCategoryClassifier(self.prompt_loader)
        self.giver = FollowUpQuestionGiver(self.prompt_loader)

        self.interview_repository = InterviewRepository(self.mongo_config)
        self.question_answer_repository = QuestionAnswerRepository(self.mongo_config)

        self.user_id = "1"
        self.interview = InterviewSession(user_id=self.user_id)
        self.interview_id = self.interview_repository.save_interview(self.interview).inserted_id

        self.initial_question = Question(content="질문 내용", feedback_score=0, question_id=None)
        self.initial_question_id = self.question_answer_repository.save_question(self.initial_question).inserted_id

        self.answer_service = AnswerService(self.interview_repository, self.question_answer_repository,
                                            self.answer_filter,
                                            self.major_classifier, self.sub_classifier, self.giver)

        self.question_content = "이 회사에서 어떻게 성과를 낼 건지 말씀해주세요."
        self.answer_content = "탁월한 개발자로서 이 회사의 핵심 인재가 되겠습니다. 그리고 신입 개발자들의 온보딩을 도움으로써 회사의 효율성을 높이는 시니어 개발자가 될 것입니다."

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.interview_repository.client.drop_database("test_database")
        self.question_answer_repository.client.drop_database("test_database")

    def test_singleton(self):
        # when
        answer_service1 = AnswerService(self.interview_repository, self.question_answer_repository, self.answer_filter,
                                        self.major_classifier, self.sub_classifier, self.giver)
        answer_service2 = AnswerService(self.interview_repository, self.question_answer_repository, self.answer_filter,
                                        self.major_classifier, self.sub_classifier, self.giver)
        # then
        self.assertEqual(answer_service1, answer_service2)

    def test_print_probability_of_followup_question(self):
        base_probability_of_question = 0.6  # 기본 확률

        num_questions_asked = 0

        for i in range(50):
            # 출제된 질문이 많아질수록 확률이 감소
            prob = base_probability_of_question / (1 + 0.1 * num_questions_asked)
            print(f"Iteration {i + 1}, Probability: {prob:.4f}")
            num_questions_asked += 1

    @patch("moview.service.answer_service.AnswerService.need_to_give_followup_question")
    def test_no_need_followup_question(self, mock_method):
        # given
        mock_method.return_value = False

        # when
        content, saved_id = self.answer_service.answer(user_id=self.user_id,
                                                       interview_id=self.interview_id,
                                                       question_id=str(ObjectId(self.initial_question_id)),
                                                       question_content=self.question_content,
                                                       answer_content=self.answer_content)

        # then
        self.assertTrue(content is None)
        self.assertTrue(saved_id is None)

    @patch("moview.service.answer_service.AnswerService.need_to_give_followup_question")
    def test_need_followup_question(self, mock_method):
        mock_method.return_value = True
        # when
        content, saved_id = self.answer_service.answer(user_id=self.user_id,
                                                       interview_id=self.interview_id,
                                                       question_id=str(ObjectId(self.initial_question_id)),
                                                       question_content=self.question_content,
                                                       answer_content=self.answer_content)

        # then
        self.assertTrue(content is not None)
        print('content', content)
        question_id = self.question_answer_repository.find_question_by_object_id(saved_id)
        self.assertEqual(str(question_id.get("_id")), str(ObjectId(saved_id)))
