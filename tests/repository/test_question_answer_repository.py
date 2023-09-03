import unittest

from bson import ObjectId
from moview.domain.entity.question_answer.answer import Answer
from moview.domain.entity.question_answer.question import Question
from moview.config.db.mongo_config import MongoConfig
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository


class TestQuestionAnswerRepository(unittest.TestCase):
    def setUp(self):
        # 테스트를 위해 테스트용 db를 생성함.
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"
        self.repository = QuestionAnswerRepository(self.mongo_config)

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.repository.client.drop_database("test_database")

    def test_singleton(self):
        # when
        repository1 = QuestionAnswerRepository(self.mongo_config)
        repository2 = QuestionAnswerRepository(self.mongo_config)

        # then
        self.assertEqual(repository1, repository2)

    def save_initial_question(self, question_content, interview_id, question_id):
        return self.repository.save_question(
            Question(content=question_content, interview_id=interview_id, feedback_score=0,
                     question_id=question_id))

    def test_save_initial_question(self):
        # given
        question_content = "질문"
        interview_id = {"_id": None}
        question_id = None

        # when
        result = self.save_initial_question(question_content, interview_id, question_id)

        # then
        found = self.repository.find_question_by_object_id(str(result.inserted_id))

        self.assertEqual(found["content"], question_content)
        self.assertEqual(found["feedback_score"], 0)
        self.assertEqual(found["interview_id"], interview_id)
        self.assertEqual(found["question_id"], None)  # 초기 질문은 아무것도 가리키면 안되므로 None

    def test_save_followup_question(self):
        # given
        initial_question = self.save_initial_question(question_content="질문", interview_id={"_id": None},
                                                      question_id=None)
        # when
        result = self.repository.save_question(Question(content="꼬리 질문", interview_id={"_id": None},
                                                        question_id={"question_id": str(
                                                            ObjectId(initial_question.inserted_id))}, feedback_score=0))

        # then
        found = self.repository.find_question_by_object_id(str(result.inserted_id))
        self.assertEqual(found["content"], "꼬리 질문")
        self.assertEqual(found["feedback_score"], 0)
        self.assertEqual(found["interview_id"], {"_id": None})
        self.assertEqual(found["question_id"],
                         {"question_id": str(ObjectId(initial_question.inserted_id))})  # 꼬리 질문은 이전 질문을 가리키고 있어야 한다.

    def test_save_answer_without_question(self):
        with self.assertRaises(ValueError):
            self.repository.save_answer(Answer(content="답변", category="category",
                                               sub_category="sub_category", question_id=None))

    def test_save_answer(self):
        # given
        initial_question = self.save_initial_question(question_content="질문", interview_id={"_id": None},
                                                      question_id=None)

        # when
        answer = self.repository.save_answer(
            Answer(content="답변", category="category", sub_category="sub_category", evaluation="good",
                   question_id={
                       "question_id": str(ObjectId(initial_question.inserted_id))}))

        # then
        found = self.repository.find_answer_by_object_id(str(answer.inserted_id))
        self.assertEqual(found["content"], "답변")
        self.assertEqual(found["category"], "category")
        self.assertEqual(found["sub_category"], "sub_category")
        self.assertEqual(found["question_id"], {"question_id": str(ObjectId(initial_question.inserted_id))})
