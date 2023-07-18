import logging
import datetime


class MongoHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET,
                 host='localhost', port=27017, username=None, password=None, authMechanism='DEFAULT',
                 databaseName='mongolog', collectionName='log', capped=True, size=100000, isCollectionDrop=False,
                 instanceName='default'):
        import pymongo
        import platform

        logging.Handler.__init__(self, level)  # // 부모 생성자 호출

        self.conn = pymongo.MongoClient(host=host, port=port,  # // 몽고클라이언트를 만든다
                                        username=username,
                                        password=password,
                                        authMechanism='DEFAULT')
        self.db = self.conn.get_database(databaseName)  # // 데이터베이스를 가져온다

        # // 데이터베이스 컬렉션을 가져온다
        if collectionName in self.db.list_collection_names():  # // 존재한다면
            if isCollectionDrop:
                self.db.drop_collection(collectionName)  # // Drop하고
                self.collection = self.create_collection(collectionName)  # // 다시 만든다
            else:
                # // 가져온다
                self.collection = self.db.get_collection(collectionName)
        else:  # // 없다면
            self.collection = self.create_collection(collectionName)  # // 만든다

        self.hostName = platform.node()  # // 호스트이름을 저장한다
        self.instanceName = instanceName  # // 인스턴스이름을 저장한다

    def create_collection(self, collectionName):
        # // 컬렉션이름으로 컬렉션을 만들고 리턴한다
        return self.db.create_collection(collectionName,
                                         capped=True,  # // 고정크기 컬렉션
                                         size=10000000)  # // 컬렉션 최대크기지정(단위: bytes)

    def emit(self, record):
        self.record = record
        document = \
            {
                'when': datetime.datetime.now(),  # // 현재일시
                'localhostName': self.hostName,  # // 로컬 호스트명
                'localInstanceName': self.instanceName,  # // 로컬 인스턴스명
                'fileName': record.filename,  # // 파일명
                'processName': record.processName,  # // 프로세스명
                'threadName': record.threadName,  # // 쓰레드명
                'functionName': record.funcName,  # // 함수명
                'levelNumber': record.levelno,  # // 로그레벨(ex. 10)
                'levelName': record.levelname,  # // 로그레벨명(ex. DEBUG)
                'message': record.msg,  # // 오류 메시지
            }
        self.collection.insert_one(document, bypass_document_validation=False)