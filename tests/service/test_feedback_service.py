import unittest
from moview.service.feedback_service import FeedbackService
from moview.config.db.mongo_config import MongoConfig
from moview.domain.entity.question_answer.question import Question
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository


class TestFeedbackService(unittest.TestCase):

    def setUp(self):
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"
        self.question_answer_repository = QuestionAnswerRepository(self.mongo_config)
        self.feedback_service = FeedbackService(self.question_answer_repository)
        self.user_id = "1"
        self.interview_id = "1"

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.question_answer_repository.client.drop_database("test_database")

    def save_question(self, question_content, question_id):
        return self.question_answer_repository.save_question(
            Question(content=question_content, feedback_score=0, prev_question_id=question_id))

    def test_singleton(self):
        # when
        feedback_service1 = FeedbackService(self.question_answer_repository)
        feedback_service2 = FeedbackService(self.question_answer_repository)
        # then
        self.assertEqual(feedback_service1, feedback_service2)

    def test_feedback(self):
        # given
        question_list = []
        for i in range(5):
            question_list.append(self.save_question(question_content=f"초기 질문{i}", question_id={
                "#ref": self.question_answer_repository.collection.name,
                "#id": None,
                "#db": self.question_answer_repository.db.name
            }))

        # when
        self.feedback_service.feedback(user_id=self.user_id, interview_id=self.interview_id,
                                       question_ids=[str(question_list[i].inserted_id) for i in range(5)],
                                       feedback_scores=["5" for i in range(5)])

        # then
        for i in range(5):
            found = self.question_answer_repository.find_question_by_object_id(str(question_list[i].inserted_id))
            self.assertEqual(found["feedback_score"], 5)
