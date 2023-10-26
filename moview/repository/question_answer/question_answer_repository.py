from bson import ObjectId
from typing import Any, Dict
from pymongo import MongoClient
from pymongo.results import InsertOneResult, UpdateResult
from moview.config.db.mongo_config import MongoConfig
from moview.utils.singleton_meta_class import SingletonMeta
from moview.domain.entity.question_answer.question import Question
from moview.domain.entity.question_answer.answer import Answer
from moview.config.loggers.mongo_logger import execution_trace_logger, error_logger
from moview.environment.environment_loader import EnvironmentLoader
from moview.config.db.mongo_constant import *


class QuestionAnswerRepository(metaclass=SingletonMeta):
    def __init__(self, mongo_config: MongoConfig):
        # 공통 MongoDB 설정
        common_config = {
            "host": EnvironmentLoader.getenv(DB_HOST),
            "port": int(EnvironmentLoader.getenv(DB_PORT)),
            "username": EnvironmentLoader.getenv(DB_USERNAME),
            "password": EnvironmentLoader.getenv(DB_PASSWORD)
        }

        # prod 환경일 경우 DocumentDB 설정
        if EnvironmentLoader.is_prod_env():
            prod_config = {
                "tls": True,
                "tlsCAFile": EnvironmentLoader.getenv(TLS_CA_FILE),
                "replicaSet": EnvironmentLoader.getenv(REPLICA_SET),
                "readPreference": EnvironmentLoader.getenv(READ_PREFERENCE),
                "retryWrites": False
            }
            common_config.update(prod_config)

        self.client = MongoClient(**common_config)
        self.db = self.client[mongo_config.db_name]
        self.collection = self.db["input_data"]

    def save_question(self, question: Question) -> InsertOneResult:
        if question.prev_question_id is None:
            execution_trace_logger(msg="SAVE_QUESTION_INITIAL", question_id=question.prev_question_id)
        else:
            execution_trace_logger(msg="SAVE_QUESTION_FOLLOW_UP", question_id=question.prev_question_id)

        return self.collection.insert_one(question.dict())

    def find_question_by_object_id(self, object_id: str) -> Dict[str, Any]:
        execution_trace_logger(msg="FIND_QUESTION_BY_OBJECT_ID", object_id=object_id)
        return self.collection.find_one({"_id": ObjectId(object_id)})

    def find_answer_by_question_id(self, question_id: Dict[str, str]) -> Dict[str, Any]:
        execution_trace_logger(msg="FIND_ANSWER_BY_QUESTION_ID", question_id=question_id)
        other_collection = self.client[question_id["#db"]][question_id["#ref"]]
        return other_collection.find_one({"question_id": question_id})

    def update_question(self, question: Dict[str, Any], object_id: str) -> None:
        execution_trace_logger(msg="UPDATE_QUESTION", object_id=object_id)
        self.collection.update_one({"_id": ObjectId(object_id)}, {"$set": question})

    def save_answer(self, answer: Answer) -> InsertOneResult:
        if answer.question_id is None:
            error_logger(msg="ERROR_IN_SAVE_ANSWER")
            raise ValueError("question_id가 None입니다. question_id는 반드시 존재해야 합니다.")

        return self.collection.insert_one(answer.dict())

    def find_answer_by_object_id(self, object_id: str) -> Dict[str, Any]:
        execution_trace_logger(msg="FIND_ANSWER_BY_OBJECT_ID", object_id=object_id)
        return self.collection.find_one({"_id": ObjectId(object_id)})

    def update_answer_by_question_id(self, answer: Dict[str, Any], question_id: Dict[str, str]) -> UpdateResult:
        execution_trace_logger(msg="UPDATE_ANSWER_BY_QUESTION_ID", question_id=question_id)
        other_collection = self.client[question_id["#db"]][question_id["#ref"]]
        other_collection.update_one({"question_id": question_id}, {"$set": answer})
