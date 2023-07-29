import datetime
import logging
import traceback

import pymongo

import moview.utils.aws_interface as aws

DB_HOST_PARAM = "db-host"
DB_PORT_PARAM = "db-port"
DB_USERNAME_PARAM = "db-username"
DB_PASSWORD_PARAM = "db-password"


class MongoHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET,
                 database_name='default', collection_name='collections',
                 capped=True, size=100 * 1024 * 1024, is_collection_drop=False):

        # 부모 생성자 호출
        logging.Handler.__init__(self, level)

        # MongoClient를 만들고, database를 가져 온다.
        self.conn = pymongo.MongoClient(host=aws.getparam(DB_HOST_PARAM),
                                        port=int(aws.getparam(DB_PORT_PARAM)),
                                        username=aws.getparam(DB_USERNAME_PARAM),
                                        password=aws.getparam(DB_PASSWORD_PARAM))

        # 데이터베이스 컬렉션을 가져온다
        if collection_name in self.db.list_collection_names():  # 만들려는 컬렉션 이름이 DB에 이미 있을 때
            if is_collection_drop:  # 컬렉션을 삭제하고 다시 만들고 싶다면
                self.db.drop_collection(collection_name)
                self.collection = self._create_collection(collection_name)
            else:  # 컬렉션을 삭제하지 않고 사용하고 싶다면
                self.collection = self.db.get_collection(collection_name)
        else:  # 만들려는 컬렉션 이름이 DB에 없을 때
            self.collection = self._create_collection(collection_name)

    def _create_collection(self, collection_name):
        # 컬렉션 이름으로 컬렉션을 만들고 리턴 한다.
        return self.db.create_collection(collection_name,
                                         capped=True,  # 고정 크기 컬렉션 (size를 넘어서면 오래된 document부터 삭제)
                                         size=100 * 1024 * 1024)  # 컬렉션 최대 크기(100MB) 지정(단위: bytes)

    def emit(self, record):
        document = {
            # session id는 추가 파라미터로 직접 추가
            'timestamp': datetime.datetime.now(),  # 시간
            'fileName': record.filename,  # 파일명
            'className': getattr(record, 'classname', '(unknown class)'),  # 클래스명
            'functionName': record.funcName,  # 함수명
            'levelName': record.levelname,  # 로그 레벨명(ex. DEBUG)
            'message': record.getMessage(),  # 메시지
        }

        # error 이상의 로그 레벨인 경우, 에러 정보를 document에 추가
        if record.levelno >= logging.ERROR:
            if record.exc_info:  # 예외 정보가 있는 경우
                # traceback 모듈을 이용하여 예외 정보를 문자열로 변환
                document['exc_info'] = ''.join(traceback.format_exception(*record.exc_info))
            if record.stack_info:  # 스택 정보가 있는 경우
                # traceback 모듈을 이용하여 스택 정보를 문자열로 변환
                document['stack_info'] = '\n'.join(traceback.StackSummary.from_list(record.stack_info).format())

        # record의 extra에 있는 모든 추가 정보를 document에 추가
        for key, value in record.__dict__.get('extra', {}).items():
            if key not in document:
                document[key] = value

        self.collection.insert_one(document, bypass_document_validation=False)
