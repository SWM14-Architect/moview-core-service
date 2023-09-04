import unittest
from unittest.mock import patch
from moview.service.answer_service import AnswerService
from moview.config.db.mongo_config import MongoConfig
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.repository.interview_repository import InterviewRepository
from moview.modules.question_generator import AnswerFilter, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver
from moview.utils.prompt_loader import PromptLoader


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
