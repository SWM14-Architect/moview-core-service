from bson import ObjectId
from typing import Any, Dict, Optional
from pymongo import MongoClient
from pymongo.results import InsertOneResult
from moview.config.db.mongo_config import MongoConfig
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.domain.entity.user.user import OauthUser


class UserRepository(metaclass=SingletonMeta):
    def __init__(self, mongo_config: MongoConfig):
        self.client = MongoClient(mongo_config.host, mongo_config.port)
        self.db = self.client[mongo_config.db_name]
        self.collection = self.db["user"]

    def upsert_user(self, user: OauthUser) -> Optional[InsertOneResult]:
        # 전에 가입한 적 없으면, 새로이 가입시키는 메서드

        execution_trace_logger(msg="UPSERT_USER", user_profile_id=user.profile_id)
        if not self.find_user_by_oauth_id(user):
            return self.collection.insert_one(user.dict())
        else:
            return None

    def find_user_by_oauth_id(self, user: OauthUser) -> Optional[Dict[str, Any]]:
        # 전에 가입한적 있는지 확인하기 위해 oauth_profile_id로 검색하는 메서드

        execution_trace_logger(msg="FIND_USER_BY_OAUTH_ID", user_profile_id=user.profile_id)
        return self.collection.find_one({"profile_id": user.profile_id})

    def find_user_by_object_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        # 가입하고 나서, user_id를 받아서 해당 user를 찾는 메서드

        execution_trace_logger(msg="FIND_USER_BY_OBJECT_ID", user_id=user_id)
        return self.collection.find_one({"_id": ObjectId(user_id)})
