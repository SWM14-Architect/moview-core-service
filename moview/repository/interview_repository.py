from bson import ObjectId
from typing import Any, Dict
from pymongo import MongoClient
from pymongo.results import UpdateResult, InsertOneResult
from moview.config.db.mongo_config import MongoConfig
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.domain.entity.interview_session_document import InterviewSession


class InterviewRepository(metaclass=SingletonMeta):
    def __init__(self, mongo_config: MongoConfig):
        self.client = MongoClient(mongo_config.host, mongo_config.port)
        self.db = self.client[mongo_config.db_name]
        self.collection = self.db["interview"]

    def save_interview(self, interview: InterviewSession) -> InsertOneResult:
        execution_trace_logger(msg="SAVE_INTERVIEW", user_id=interview.user_id)
        return self.collection.insert_one(interview.dict())

    def find_interview_by_object_id(self, user_id: str, interview_id) -> Dict[str, Any]:
        execution_trace_logger(msg="FIND_INTERVIEW_BY_OBJECT_ID", user_id=user_id, interview_id=interview_id)
        return self.collection.find_one({"user_id": user_id, "_id": ObjectId(interview_id)})

    def update_interview(self, interview: Dict[str, Any], object_id: str) -> UpdateResult:
        execution_trace_logger(msg="UPDATE_INTERVIEW", object_id=object_id)
        return self.collection.update_one({"_id": ObjectId(object_id)}, {"$set": interview})
