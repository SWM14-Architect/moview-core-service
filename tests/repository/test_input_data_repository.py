import unittest

from moview.config.db.mongo_config import MongoConfig
from moview.domain.entity.input_data.coverletter_document import CoverLetter
from moview.domain.entity.input_data.initial_input_data_document import InitialInputData
from moview.repository.input_data_repository import InputDataRepository


class TestInputDataRepository(unittest.TestCase):
    def setUp(self):
        # 테스트를 위해 테스트용 db를 생성함.
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"
        self.repository = InputDataRepository(self.mongo_config)

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.repository.client.drop_database("test_database")

    def test_singleton(self):
        # when
        repository1 = InputDataRepository(self.mongo_config)
        repository2 = InputDataRepository(self.mongo_config)

        # then
        self.assertEqual(repository1, repository2)  # repository1과 repository2가 같은 객체인지 확인

    def test_save(self):

        # given
        test_initial_input_data_model = InitialInputData(
            interviewee_name="test", company_name="test", job_group="test", recruit_announcement="test"
        )
        test_cover_letter_model_list = [
            CoverLetter(
                coverletter_question=f"test{i}",
                coverletter_answer=f"test{i}",
                coverletter_analysis_result=f"test{i}"
            ) for i in range(3)
        ]

        # when
        test_document = self.repository.save(test_initial_input_data_model, test_cover_letter_model_list)

        # then
        self.assertNotEqual(test_document.inserted_id, None) # inserted_id는 insert가 성공했을 때, 해당 document의 id를 나타냄.
        self.assertEqual(test_document.acknowledged, True) # acknowledged는 insert가 성공했는지 여부를 나타냄.

        retrieved_document = self.repository.collection.find_one({"_id": test_document.inserted_id})
        self.assertNotEqual(retrieved_document, None)
        self.assertEqual(retrieved_document["interviewee_name"], "test")
        self.assertEqual(retrieved_document["company_name"], "test")
        self.assertEqual(retrieved_document["job_group"], "test")
        self.assertEqual(retrieved_document["recruit_announcement"], "test")
        self.assertEqual(len(retrieved_document["interview_id_list"]), 3)

    def test_find_by_object_id(self):
        # when
        test_initial_input_data_model = InitialInputData(
            interviewee_name="find_test", company_name="find_test", job_group="find_test", recruit_announcement="find_test"
        )
        test_cover_letter_model_list = [
            CoverLetter(
                coverletter_question=f"test{i}",
                coverletter_answer=f"test{i}",
                coverletter_analysis_result=f"test{i}"
            ) for i in range(2)
        ]
        test_document = self.repository.save(test_initial_input_data_model, test_cover_letter_model_list)

        # when
        entity = self.repository.find_by_object_id(test_document.inserted_id)

        # then
        self.assertEqual(entity["interviewee_name"], "find_test")
        self.assertEqual(entity["company_name"], "find_test")
        self.assertEqual(entity["job_group"], "find_test")
        self.assertEqual(entity["recruit_announcement"], "find_test")
        self.assertEqual(len(entity["interview_id_list"]), 2)
