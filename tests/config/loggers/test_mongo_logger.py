# import unittest
# from unittest.mock import patch, Mock
# import logging
#
# from moview.loggers.mongo_logger import MongoLogger, CustomLogRecord
#
#
# class TestMongoLogger(unittest.TestCase):
#
#     def test_execution_trace_logger(self):
#         with patch('moview.loggers.mongo_logger.MongoHandler') as mock_mongo_handler:
#             # given
#             mock_mongo_handler.return_value.level = logging.INFO
#
#             mongo_logger_instance = MongoLogger()
#             execution_trace_logger_instance = mongo_logger_instance.execution_trace_logger
#             mongo_logger_instance.execution_trace_logger.logger.handlers.clear()
#
#             print(execution_trace_logger_instance.logger.isEnabledFor(logging.INFO))
#             print(execution_trace_logger_instance.logger.handlers)
#
#             # when
#             execution_trace_logger_instance("test")
#
#             # then
#             mock_mongo_handler.return_value.emit.assert_called_once()
#
#             # Print calls made to the emit method
#             print("Calls made to emit:", mock_mongo_handler.return_value.emit.call_args_list)
#
#             # MongoHandler의 emit 메소드의 첫 번째 인자를 가져와서 LogRecord를 확인
#             emitted_record = mock_mongo_handler.return_value.emit.call_args[0][0]
#
#             self.assertIsInstance(emitted_record, CustomLogRecord)
#             self.assertEqual(emitted_record.filename, "test_mongo_logger.py")
#             self.assertEqual(emitted_record.classname, "TestMongoLogger")
#             self.assertEqual(emitted_record.funcName, "test_execution_trace_logger")
#             self.assertEqual(emitted_record.levelname, "INFO")
#             self.assertEqual(emitted_record.msg, "test")
#
#     # def test_execution_trace_logger(self):
#     #     with patch('moview.handlers.mongo_handler.MongoHandler') as mock_mongo_handler:
#     #         # given
#     #         mock_mongo_handler.return_value.level = logging.INFO
#     #
#     #         mongo_logger_instance = MongoLogger()
#     #         execution_trace_logger_instance = mongo_logger_instance.execution_trace_logger
#     #
#     #         print(execution_trace_logger_instance.logger.isEnabledFor(logging.INFO))
#     #         print(execution_trace_logger_instance.logger.handlers)
#     #
#     #         # when
#     #         execution_trace_logger_instance("test")
#     #
#     #         # then
#     #         mock_mongo_handler.return_value.emit.assert_called_once()
#     #
#     #         # MongoHandler의 emit 메소드의 첫 번째 인자를 가져와서 LogRecord를 확인
#     #         emitted_record = mock_mongo_handler.return_value.emit.call_args[0][0]
#     #
#     #         self.assertIsInstance(emitted_record, CustomLogRecord)
#     #         self.assertEqual(emitted_record.filename, "test_mongo_logger.py")
#     #         self.assertEqual(emitted_record.classname, "TestMongoLogger")
#     #         self.assertEqual(emitted_record.funcName, "test_execution_trace_logger")
#     #         self.assertEqual(emitted_record.levelname, "INFO")
#     #         self.assertEqual(emitted_record.msg, "test")
#
#     def test_error_logger(self):
#         with patch('moview.loggers.mongo_logger.MongoHandler') as mock_mongo_handler:
#             # Mock the record that would be generated by the logger
#             log_record = Mock()
#             log_record.levelname = 'ERROR'
#             log_record.msg = 'test error message'
#
#             # Call the logger with a message
#             error_logger("test error message")
#
#             # Assertions
#             mock_mongo_handler.assert_called_once_with(level=log_record.levelname,
#                                                        database_name='log',
#                                                        collection_name='errorLogs')
#             mock_mongo_handler.return_value.emit.assert_called_once_with(log_record)
#
#     def test_prompt_result_logger(self):
#         with patch('moview.loggers.mongo_logger.MongoHandler') as mock_mongo_handler:
#             # Mock the record that would be generated by the logger
#             log_record = Mock()
#             log_record.levelname = 'INFO'
#             log_record.msg = 'test prompt result message'
#
#             # Call the logger with a message
#             prompt_result_logger("test prompt result message")
#
#             # Assertions
#             mock_mongo_handler.assert_called_once_with(level=log_record.levelname,
#                                                        database_name='log',
#                                                        collection_name='promptResultLogs')
#             mock_mongo_handler.return_value.emit.assert_called_once_with(log_record)