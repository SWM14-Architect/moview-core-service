import unittest
from moview.config.db.mongo_config import MongoConfig
from moview.domain.entity.user.user_document import OauthUser
from moview.repository.user.user_repository import UserRepository


class TestUserRepository(unittest.TestCase):
    def setUp(self):
        # 테스트를 위해 테스트용 db를 생성함.
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "test_database"
        self.repository = UserRepository(self.mongo_config)

        self.test_user = OauthUser(
            profile_id="test",
            profile_nickname="test",
            profile_image_url="test",
            thumbnail_image_url="test")

    def tearDown(self):
        # 테스트용 db를 삭제함.
        self.repository.client.drop_database("test_database")

    def test_singleton(self):
        # when
        repository1 = UserRepository(self.mongo_config)
        repository2 = UserRepository(self.mongo_config)

        # then
        self.assertEqual(repository1, repository2)

    def test_upsert_user_if_not_in_db(self):
        # when
        test_document = self.repository.upsert_user(self.test_user)

        # then
        self.assertNotEqual(test_document.inserted_id, None)
        self.assertEqual(test_document.acknowledged, True)

    def test_find_user_by_object_id(self):
        # given
        saved_document = self.repository.upsert_user(self.test_user)

        # when
        retrieved_document = self.repository.find_user_by_object_id(saved_document.inserted_id)

        # then
        self.assertEqual(retrieved_document["profile_id"], "test")
        self.assertEqual(retrieved_document["profile_nickname"], "test")
        self.assertEqual(retrieved_document["profile_image_url"], "test")
        self.assertEqual(retrieved_document["thumbnail_image_url"], "test")

    def test_upsert_user_if_in_db(self):
        # given
        self.repository.upsert_user(self.test_user)

        # when
        test_document = self.repository.upsert_user(self.test_user)

        # then
        self.assertEqual(test_document, None)
