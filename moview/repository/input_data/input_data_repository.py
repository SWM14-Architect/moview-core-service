from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.results import InsertOneResult

from moview.config.db.mongo_config import MongoConfig
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.domain.entity.input_data.coverletter_document import CoverLetter
from moview.domain.entity.input_data.initial_input_data_document import InitialInputData
from moview.utils.singleton_meta_class import SingletonMeta
from bson import ObjectId
from moview.environment.environment_loader import EnvironmentLoader
from moview.config.db.mongo_constant import *


class InputDataRepository(metaclass=SingletonMeta):
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

    def save(self, initial_input_data: InitialInputData, cover_letter_list: List[CoverLetter]) -> InsertOneResult:
        for cover_letter in cover_letter_list:
            cover_letter_model = cover_letter.dict()
            cover_letter_document_id = str(self.collection.insert_one(cover_letter_model).inserted_id)

            # InitalInputData에 cover_letter_document_id를 추가함.
            initial_input_data.coverletter_id_list.append({
                "#ref": self.collection.name,
                "#id": cover_letter_document_id,
                "#db": self.db.name
            })

        initial_input_data_model = initial_input_data.dict()
        execution_trace_logger(msg="SAVE_INITIAL_INPUT_DATA")
        return self.collection.insert_one(initial_input_data_model)

    def save_for_light_mode(self, initial_input_data: InitialInputData) -> InsertOneResult:
        initial_input_data_model = initial_input_data.dict()
        execution_trace_logger(msg="SAVE_INITIAL_INPUT_DATA_FOR_LIGHT_MODE")
        return self.collection.insert_one(initial_input_data_model)

    def find_cover_letter_by_object_id(self, coverletter_id: Dict[str, Optional[str]]) -> Optional[Dict[str, Any]]:
        execution_trace_logger(msg="FIND_COVER_LETTER_BY_OBJECT_ID", object_id=coverletter_id["#id"])
        # "#db"와 "#ref"를 이용해 document가 있는 collection에 접속함.
        other_collection = self.client[coverletter_id["#db"]][coverletter_id["#ref"]]
        return other_collection.find_one({"_id": ObjectId(coverletter_id["#id"])})

    def find_input_data_by_object_id(self, object_id: str) -> Dict[str, Any]:
        execution_trace_logger(msg="FIND_INPUT_DATA_BY_OBJECT_ID", object_id=object_id)

        document = self.collection.find_one({"_id": ObjectId(object_id)})
        coverletter_id_list = document["coverletter_id_list"]

        document["coverletter_document"] = []
        for coverletter_id in coverletter_id_list:
            coverletter_document = self.find_cover_letter_by_object_id(coverletter_id)
            document["coverletter_document"].append(coverletter_document)
        return document

    def find_input_data_by_interviewee_name(self, interviewee_name: str) -> Optional[Dict[str, Any]]:
        execution_trace_logger(msg="FIND_INPUT_DATA_BY_INTERVIEWEE_NAME", interviewee_name=interviewee_name)
        document = self.collection.find_one({"interviewee_name": interviewee_name})
        coverletter_id_list = document["coverletter_id_list"]

        document["coverletter_document"] = []
        for coverletter_id in coverletter_id_list:
            coverletter_document = self.find_cover_letter_by_object_id(coverletter_id)
            document["coverletter_document"].append(coverletter_document)
        return document
