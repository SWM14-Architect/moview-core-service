from bson import ObjectId
from typing import Any, Dict
from pymongo import MongoClient
from pymongo.results import UpdateResult, InsertOneResult
from moview.config.db.mongo_config import MongoConfig
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.domain.entity.interview_document import Interview
from moview.environment.environment_loader import EnvironmentLoader
from moview.config.db.mongo_constant import DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD


class InterviewRepository(metaclass=SingletonMeta):
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

    def save_interview(self, interview: Interview) -> InsertOneResult:
        execution_trace_logger(msg="SAVE_INTERVIEW")
        return self.collection.insert_one(interview.dict())

    def find_interview_by_object_id(self, user_id: str, interview_id) -> Dict[str, Any]:
        execution_trace_logger(msg="FIND_INTERVIEW_BY_OBJECT_ID")
        return self.collection.find_one({"user_id": user_id, "_id": ObjectId(interview_id)})

    def update_interview(self, interview_model: Interview, interview_id: str) -> UpdateResult:
        execution_trace_logger(msg="UPDATE_INTERVIEW", object_id=interview_id)
        return self.collection.update_one({"_id": ObjectId(interview_id)}, {"$set": interview_model.dict()})
