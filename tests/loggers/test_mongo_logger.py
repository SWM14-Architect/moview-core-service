import unittest
from unittest.mock import patch, MagicMock
from moview.handlers.mongo_handler import MongoHandler
from moview.loggers.mongo_logger import MongoLogger


class TestMongoLogger(unittest.TestCase):
    @patch('moview.loggers.mongo_logger.MongoHandler', autospec=True)
    def setUp(self, mock_mongo_handler):
        self.mock_mongo_handler = mock_mongo_handler
        self.mongo_logger = MongoLogger()

        self.execution_trace_logger = self.mongo_logger.execution_trace_logger
        self.error_logger = self.mongo_logger.error_logger
        self.prompt_result_logger = self.mongo_logger.prompt_result_logger

    def test_execution_trace_logger(self):
        """
        execution_trace_logger에 각 입력 케이스에 대해서, 정상적으로 CustomLogRecord가 생성되는지 테스트
        """
        # # 테스트용 CustomLogRecord 객체 생성
        # log_record = MagicMock()
        # log_record.levelname = 'INFO'
        # log_record.msg = 'test message'
        # log_record.args = None
        # log_record.kwargs = {'caller_frame': MagicMock()}
        #
        # # execution_trace_logger 호출
        # self.execution_trace_logger(log_record)
        #
        # # CustomLogRecord 생성 확인
        # self.mock_mongo_handler.assert_called_once_with(level=log_record.levelname,
        #                                                 database_name='log',
        #                                                 collection_name='executionTraceLogs')
        # self.mock_mongo_handler.return_value.emit.assert_called_once_with(log_record)


if __name__ == "__main__":
    unittest.main()
