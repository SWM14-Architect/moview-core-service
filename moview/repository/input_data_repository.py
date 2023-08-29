from typing import Any, Dict, List

from pymongo import MongoClient
from pymongo.results import InsertOneResult

from moview.config.db.mongo_config import MongoConfig
from moview.domain.entity.input_data.coverletter_document import CoverLetter
from moview.domain.entity.input_data.initial_input_data_document import InitialInputData
from moview.utils.singleton_meta_class import SingletonMeta
from bson import ObjectId


class InputDataRepository(metaclass=SingletonMeta):
    def __init__(self, mongo_config: MongoConfig):
        self.client = MongoClient(mongo_config.host, mongo_config.port)
        self.db = self.client[mongo_config.db_name]
        self.collection = self.db["input_data"]

    def save(
            self,
            initial_input_data: InitialInputData,
            cover_letter_list: List[CoverLetter]
    ) -> InsertOneResult:
        for cover_letter in cover_letter_list:
            cover_letter_model = cover_letter.dict()
            cover_letter_document_id = str(self.collection.insert_one(cover_letter_model).inserted_id)

            # InitalInputData에 cover_letter_document_id를 추가함.
            initial_input_data.interview_id_list.append({
                "#ref": self.collection.name,
                "#id": cover_letter_document_id,
                "#db": self.db.name
            })

        initial_input_data_model = initial_input_data.dict()
        return self.collection.insert_one(initial_input_data_model)

    def find_by_object_id(self, object_id: str) -> Dict[str, Any]:
        document = self.collection.find_one({"_id": ObjectId(object_id)})
        interview_id_list = document["interview_id_list"]

        document["interview_document"] = []
        for interview_id in interview_id_list:
            # "#db"와 "#ref"를 이용해 document가 있는 collection에 접속함.
            other_collection = self.client[interview_id["#db"]][interview_id["#ref"]]
            document["interview_document"].append(other_collection.find_one({"_id": ObjectId(interview_id["#id"])}))
        return document
