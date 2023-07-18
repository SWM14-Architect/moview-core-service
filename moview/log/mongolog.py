import os
import sys
import logging
import pymongo
import datetime


class MongoHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET,
                 databaseName='mongolog', collectionName='log',
                 capped=True, size=100000, isCollectionDrop=False):

        # 부모 생성자 호출
        logging.Handler.__init__(self, level)

        # MongoClient를 만들고, database를 가져온다
        if sys.platform == 'darwin':
            # MacOS
            self.conn = pymongo.MongoClient(host=os.environ["CORE_DEV_DB_HOST"],
                                            port=os.environ["CORE_DEV_DB_PORT"],
                                            username=os.environ["CORE_DEV_DB_USERNAME"],
                                            password=os.environ["CORE_DEV_DB_PASSWORD"])
            self.db = self.conn.get_database(databaseName)
        elif sys.platform == 'win32' or sys.platform == 'linux':
            # Windows, linux
            self.conn = pymongo.MongoClient(host=os.getenv("CORE_DEV_DB_HOST"),
                                            port=os.getenv("CORE_DEV_DB_PORT"),
                                            username=os.getenv("CORE_DEV_DB_USERNAME"),
                                            password=os.getenv("CORE_DEV_DB_PASSWORD"))
            self.db = self.conn.get_database(databaseName)

        # 데이터베이스 컬렉션을 가져온다
        if collectionName in self.db.list_collection_names():  # 존재한다면
            if isCollectionDrop:
                self.db.drop_collection(collectionName)  # Drop하고
                self.collection = self.create_collection(collectionName)  # 다시 만든다
            else:
                self.collection = self.db.get_collection(collectionName)
        else:
            self.collection = self.create_collection(collectionName)

    def create_collection(self, collectionName):
        # 컬렉션이름으로 컬렉션을 만들고 리턴한다
        return self.db.create_collection(collectionName,
                                         capped=True,  # 고정크기 컬렉션
                                         size=10000000)  # 컬렉션 최대크기지정(단위: bytes)

    def emit(self, record):
        self.record = record
        document = \
            {
                'when': datetime.datetime.now(),  # 현재일시
                'fileName': record.filename,  # 파일명
                'processName': record.processName,  # 프로세스명
                'threadName': record.threadName,  # 쓰레드명
                'functionName': record.funcName,  # 함수명
                'levelNumber': record.levelno,  # 로그레벨(ex. 10)
                'levelName': record.levelname,  # 로그레벨명(ex. DEBUG)
                'message': record.msg,  # 오류 메시지
            }
        self.collection.insert_one(document, bypass_document_validation=False)
