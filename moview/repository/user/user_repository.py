from bson import ObjectId
from typing import Any, Dict, Optional
from pymongo import MongoClient
from pymongo.results import InsertOneResult
from moview.config.db.mongo_config import MongoConfig
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.domain.entity.user.user import OauthUser
from moview.config.db.mongo_constant import *
from moview.environment.environment_loader import EnvironmentLoader


class UserRepository(metaclass=SingletonMeta):
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
        self.collection = self.db["user"]

    def upsert_user(self, user: OauthUser) -> Optional[InsertOneResult]:
        # 전에 가입한 적 없으면, 새로이 가입시키는 메서드
        execution_trace_logger(msg="UPSERT_USER")
        if not self.find_user_by_oauth_id(user):
            return self.collection.insert_one(user.dict())
        else:
            return None

    def find_user_by_oauth_id(self, user: OauthUser) -> Optional[Dict[str, Any]]:
        # 전에 가입한적 있는지 확인하기 위해 oauth_profile_id로 검색하는 메서드.
        execution_trace_logger(msg="FIND_USER_BY_OAUTH_ID")
        return self.collection.find_one({"profile_id": user.profile_id})

    def find_user_by_profile_id_for_jwt(self, user_profile_id: str) -> Optional[Dict[str, Any]]:
        # jwt에 담긴 identity를 이용해서 user를 찾는 메서드. identity는 profile_id이다. oauth_controller의 kakao_oauth_controller의 get 메서드를 보면 알 수 있다.
        execution_trace_logger(msg="FIND_USER_BY_PROFILE_ID_FOR_JWT")
        return self.collection.find_one({"profile_id": user_profile_id})

    def find_user_by_object_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        # 가입하고 나서, user_id를 받아서 해당 user를 찾는 메서드(테스트 용도)
        execution_trace_logger(msg="FIND_USER_BY_OBJECT_ID")
        return self.collection.find_one({"_id": ObjectId(user_id)})
