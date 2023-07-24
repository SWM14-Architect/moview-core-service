import datetime
import logging
import os
import unittest
from unittest import TestCase, mock

import mongomock

from moview.handlers.mongo_handler import MongoHandler


class TestMongoHandler(TestCase):
    @mock.patch('pymongo.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        # 테스트 시작 전에 임시 MongoDB 서버 생성
        self.db_name = 'test_database'  # 임시 데이터베이스 이름
        self.collection_name = 'test_collection'  # 테스트용 컬렉션 이름

        # mongomock은 capped와 size 옵션을 허용하지 않기 때문에, MongoHandler.create_collection() 메소드를 mock.patch로 대체
        with mock.patch.object(MongoHandler, '_create_collection',
                               lambda self, collection_name: self.db.create_collection(collection_name)):
            # 테스트용 MongoHandler 객체 생성
            self.handler = MongoHandler(level=logging.INFO,
                                        database_name=self.db_name,
                                        collection_name=self.collection_name)

        # 테스트용 logger 생성
        self.logger = logging.getLogger('test_logger')
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    @mock.patch('pymongo.MongoClient', new=mongomock.MongoClient)
    def test_emit(self):
        # emit() 메소드 테스트
        self.logger.info('test message')  # info() 메소드가 handler.emit() 메소드를 호출합니다.

        # 컬렉션이 생성되었는지 테스트
        self.assertIn(self.collection_name, self.handler.db.list_collection_names())

        # document가 삽입되었는지 테스트
        documents = list(self.handler.db[self.collection_name].find())
        self.assertEqual(len(documents), 1)  # 하나의 문서가 삽입 됐는지 확인
        self.assertIsInstance(documents[0]['timestamp'], datetime.datetime)  # timestamp가 datetime 타입인지 확인
        self.assertEqual(documents[0]['fileName'], os.path.basename(__file__))  # fileName이 현재 파일의 이름과 일치하는지 확인
        self.assertEqual(documents[0]['className'], '(unknown class)') # className이 '(unknown class)'인지 확인 (기본 logger는 클래스명을 가져오지 못함)
        self.assertEqual(documents[0]['functionName'], 'test_emit')  # functionName이 'test_emit'인지 확인
        self.assertEqual(documents[0]['levelName'], 'INFO')  # levelName이 'INFO'인지 확인
        self.assertEqual(documents[0]['message'], 'test message')  # message가 'test message'인지 확인


if __name__ == '__main__':
    unittest.main()
