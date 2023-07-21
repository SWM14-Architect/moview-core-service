import unittest
from unittest.mock import patch, Mock
import logging
from moview.loggers.mongo_logger import MongoLogger


class TestMongoLogger(unittest.TestCase):
    @patch('moview.handlers.mongo_handler.MongoHandler', autospec=True)
    def test_execution_trace_logger_creation(self, mock_mongo_handler):
        logger = MongoLogger()

        self.assertIsNotNone(logger.execution_trace_logger)
        self.assertEqual(logger.execution_trace_logger.level, logging.INFO)
        mock_mongo_handler.assert_called_once_with('log', 'executionTraceLogs', logging.INFO)

    @patch('moview.handlers.mongo_handler.MongoHandler', autospec=True)
    def test_error_logger_creation(self, mock_mongo_handler):
        logger = MongoLogger()

        self.assertIsNotNone(logger.error_logger)
        self.assertEqual(logger.error_logger.level, logging.ERROR)
        mock_mongo_handler.assert_called_once_with('log', 'errorLogs', logging.ERROR)

    @patch('moview.handlers.mongo_handler.MongoHandler', autospec=True)
    def test_prompt_result_logger_creation(self, mock_mongo_handler):
        logger = MongoLogger()

        self.assertIsNotNone(logger.prompt_result_logger)
        self.assertEqual(logger.prompt_result_logger.level, logging.INFO)
        mock_mongo_handler.assert_called_once_with('log', 'promptResultLogs', logging.INFO)

    @patch('moview.handlers.mongo_handler.MongoHandler.emit', new_callable=Mock)
    def test_log_execution_trace(self, mock_emit):
        logger = MongoLogger()
        message = 'test execution trace message'
        logger.log_execution_trace(message)

        # 호출된 로그 메세지가 'test execution trace message'인지 확인
        call_args = mock_emit.call_args[0][0]
        self.assertEqual(call_args.message, message)
        self.assertEqual(call_args.levelno, logging.INFO)
        self.assertEqual(logger.execution_trace_logger.handlers[0].db_name, 'log')
        self.assertEqual(logger.execution_trace_logger.handlers[0].collection_name, 'executionTraceLogs')

    @patch('moview.handlers.mongo_handler.MongoHandler.emit', new_callable=Mock)
    def test_log_error(self, mock_emit):
        logger = MongoLogger()
        message = 'test error message'
        logger.log_error(message)

        # 호출된 로그 메세지가 'test error message'인지 확인
        call_args = mock_emit.call_args[0][0]
        self.assertEqual(call_args.message, message)
        self.assertEqual(call_args.levelno, logging.ERROR)
        self.assertEqual(logger.error_logger.handlers[0].db_name, 'log')
        self.assertEqual(logger.error_logger.handlers[0].collection_name, 'errorLogs')

    @patch('moview.handlers.mongo_handler.MongoHandler.emit', new_callable=Mock)
    def test_log_prompt_result(self, mock_emit):
        logger = MongoLogger()
        message = 'test prompt result message'
        logger.log_prompt_result(message)

        # 호출된 로그 메세지가 'test prompt result message'인지 확인
        call_args = mock_emit.call_args[0][0]
        self.assertEqual(call_args.message, message)
        self.assertEqual(call_args.levelno, logging.INFO)
        self.assertEqual(logger.prompt_result_logger.handlers[0].db_name, 'log')
        self.assertEqual(logger.prompt_result_logger.handlers[0].collection_name, 'promptResultLogs')


if __name__ == "__main__":
    unittest.main()
