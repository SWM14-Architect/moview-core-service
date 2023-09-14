import asynctest
from pprint import pprint

from moview.config.db.mongo_config import MongoConfig
from moview.utils.prompt_loader import PromptLoader

from moview.modules.answer_evaluator.answer_evaluator import AnswerEvaluator
from moview.service.evaluation_service import EvaluationService
from moview.repository.interview_repository import InterviewRepository
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.domain.entity.interview_session_document import InterviewSession
from moview.domain.entity.question_answer.question import Question
from moview.domain.entity.question_answer.answer import Answer


class TestEvaluationService(asynctest.TestCase):
    def setUp(self):
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"
        self.prompt_loader = PromptLoader()

        self.interview_repository = InterviewRepository(mongo_config=self.mongo_config)
        self.question_answer_repository = QuestionAnswerRepository(mongo_config=self.mongo_config)
        self.answer_evaluator = AnswerEvaluator(prompt_loader=self.prompt_loader)
        self.evaluation_service = EvaluationService(interview_repository=self.interview_repository,
                                                    question_answer_repository=self.question_answer_repository,
                                                    answer_evaluator=self.answer_evaluator)

        self.question_answer_num = 10
        self.question_id_list = []
        for i in range(self.question_answer_num):
            # 질문 n개 저장
            self.question_content = "이 회사에서 어떻게 성과를 낼 건지 말씀해주세요."
            self.question = Question(content=self.question_content,
                                     feedback_score=0)
            self.question_id = str(self.question_answer_repository.save_question(self.question).inserted_id)
            self.question_id_list.append({
                "#ref": self.question_answer_repository.collection.name,
                "#id": self.question_id,
                "#db": self.question_answer_repository.db.name
            })

            # 답변 n개 저장
            self.answer_content = "탁월한 개발자로서 이 회사의 핵심 인재가 되겠습니다. 그리고 신입 개발자들의 온보딩을 도움으로써 회사의 효율성을 높이는 시니어 개발자가 될 것입니다."
            self.answer = Answer(content=self.answer_content,
                                 question_id={
                                     "#ref": self.question_answer_repository.collection.name,
                                     "#id": self.question_id,
                                     "#db": self.question_answer_repository.db.name
                                 })
            self.question_answer_repository.save_answer(self.answer)

        self.user_id = "1"
        self.interview = InterviewSession(user_id=self.user_id,
                                          question_id_list=self.question_id_list)
        self.interview_id = str(self.interview_repository.save_interview(self.interview).inserted_id)

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.interview_repository.client.drop_database("test_database")
        self.question_answer_repository.client.drop_database("test_database")

    async def test_evaluate_single_answer_of_interviewee(self):
        # given
        question_id = self.question_id_list[0]

        # when
        evaluated_question, evaluated_answer, evaluation_result = await self.evaluation_service._evaluate_single_answer_of_interviewee(question_id=question_id)

        # then
        answer_dict = self.question_answer_repository.find_answer_by_question_id(question_id)
        evaluation = answer_dict["evaluation"]

        pprint(evaluation)
        self.assertTrue(len(evaluation) == 2)
        self.assertTrue(evaluation[0] != "")
        self.assertTrue(evaluation[1] != "")

        self.assertEqual(evaluated_question, self.question_content)
        self.assertEqual(evaluated_answer, self.answer_content)
        self.assertEqual(evaluation_result, evaluation)

    async def test_evaluate_answers_of_interviewee(self):
        # when
        result = await self.evaluation_service.evaluate_answers_of_interviewee(user_id=self.user_id,
                                                                               interview_id=self.interview_id)
        # then
        answer_dict = [self.question_answer_repository.find_answer_by_question_id(question_id=question_id) for question_id in self.question_id_list]
        evaluation_list = [answer["evaluation"] for answer in answer_dict]

        pprint(evaluation_list)
        self.assertTrue(len(evaluation_list) == self.question_answer_num)
        self.assertTrue(len(evaluation_list[0]) == 2)
        self.assertTrue(evaluation_list[0][0] != "")
        self.assertTrue(evaluation_list[0][1] != "")

        self.assertTrue(len(result) == self.question_answer_num)
        self.assertEqual(result[0][0], self.question_content)
        self.assertEqual(result[0][1], self.answer_content)
        self.assertEqual(result[0][2], evaluation_list[0])
