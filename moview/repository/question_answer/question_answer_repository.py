from bson import ObjectId
from typing import Any, Optional, Dict
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

    def save_question(self, question_content: Any, interview_id: Dict[str, Optional[str]],
                      question_id: Optional[Dict[str, Optional[str]]]) -> InsertOneResult:

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

    def find_question_by_object_id(self, object_id: str) -> Dict[str, Any]:
        return self.collection.find_one({"_id": ObjectId(object_id)})

    def save_answer(self, answer: Answer) -> InsertOneResult:
        if answer.question_id is None:
            raise ValueError("question_id가 None입니다. question_id는 반드시 존재해야 합니다.")

        return self.collection.insert_one(answer.dict())

    def find_answer_by_object_id(self, object_id: str) -> Dict[str, Any]:
        return self.collection.find_one({"_id": ObjectId(object_id)})
