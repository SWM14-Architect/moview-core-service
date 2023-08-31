from datetime import datetime
from typing import Any, Optional
from pymongo import MongoClient
from pymongo.results import InsertOneResult
from moview.config.db.mongo_config import MongoConfig
from moview.utils.singleton_meta_class import SingletonMeta
from moview.domain.entity.question_answer.question import Question
from moview.domain.entity.question_answer.answer import Answer


class QuestionAnswerRepository(metaclass=SingletonMeta):
    def __init__(self, mongo_config: MongoConfig):
        self.client = MongoClient(mongo_config.host, mongo_config.port)
        self.db = self.client[mongo_config.db_name]
        self.collection = self.db["question_answer"]

    def save_question(self, question_content: Any, interview_id: str, question_id: Optional[str]) -> InsertOneResult:

        if question_id is None:
            # 초기 질문인 경우, question_id = None
            initial_question = Question(content=question_content, feedback_score=0, interview_id=interview_id,
                                        question_id=None)
            return self.collection.insert_one(initial_question.dict())
        else:
            # 꼬리 질문인 경우, 이전 question을 가리킴.
            followup_question = Question(content=question_content, feedback_score=0, interview_id=interview_id,
                                         question_id=question_id)

            return self.collection.insert_one(followup_question.dict())

    def save_answer(self, answer_content: Any, category: str, sub_category: str, question_id: str) -> InsertOneResult:

        # answer와 question의 관계를 맺기 위해 question_id를 저장
        answer = Answer(content=answer_content, category=category, sub_category=sub_category, evaluation="",
                        question_id=question_id)

        return self.collection.insert_one(answer.dict())
