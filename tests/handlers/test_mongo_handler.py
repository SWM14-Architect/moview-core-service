import unittest
from unittest import TestCase, mock
import logging
from moview.handlers.mongo_handler import MongoHandler
import mongomock


class TestMongoHandler(TestCase):
    @mock.patch('pymongo.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        # 테스트 시작 전에 임시 MongoDB 서버 생성
        self.db_name = 'test_database'  # 임시 데이터베이스 이름
        self.collection_name = 'test_collection'  # 테스트용 컬렉션 이름
        self.client = mongomock.MongoClient()  # 가상의 MongoDB 클라이언트 생성
        self.db = self.client[self.db_name]  # 가상의 MongoDB DB 생성

        def create_collection(self, collection_name):
            # 테스트 환경에서는 capped와 size 옵션 무시
            return self.db.create_collection(collection_name)

        # MongoHandler.create_collection() 메소드를 create_collection() 메소드를 mock으로 대체
        with mock.patch.object(MongoHandler, 'create_collection', create_collection):
            # 테스트용 MongoHandler 객체 생성
            self.handler = MongoHandler(level=logging.INFO,
                                        database_name='test_database',
                                        collection_name=self.collection_name)

        # insert_one 메소드를 mock 객체로 대체 (훔쳐오기)
        self.mock_insert = mock.Mock()
        self.handler.collection.insert_one = self.mock_insert

        # 테스트용 LogRecord 객체 생성
        self.record = logging.LogRecord(name='test', level=logging.INFO, pathname=None,
                                        lineno=0, msg='test message', args=None, exc_info=None)

    @mock.patch('pymongo.MongoClient', new=mongomock.MongoClient)
    def test_emit(self):
        # emit() 메소드 테스트
        self.handler.emit(self.record)

        # insert_one 메소드가 호출되었는지 확인
        self.mock_insert.assert_called_once()

        # insert_one에 전달된 인자가 예상한 로그 메시지를 포함하고 있는지 확인
        args, _ = self.mock_insert.call_args  # insert_one에 전달된 인자를 가져옴
        self.assertEqual(args[0]['level'], self.record.levelno)
        self.assertEqual(args[0]['message'], self.record.msg)


if __name__ == '__main__':
    unittest.main()
