import inspect
import logging
from moview.handlers.mongo_handler import MongoHandler


class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        calling_class = inspect.currentframe().f_back.f_locals.get('self', None).__class__.__name__
        extra["className"] = calling_class
        kwargs["extra"] = extra
        return msg, kwargs


class MongoLogger:
    def __init__(self):
        self.db_name = 'log'
        self.execution_trace_logger = self.__create_logger(logger_name='execution_trace_logger',
                                                           collection_name='executionTraceLogs',
                                                           log_level=logging.INFO)
        self.error_logger = self.__create_logger(logger_name='error_logger',
                                                 collection_name='errorLogs',
                                                 log_level=logging.ERROR)
        self.prompt_result_logger = self.__create_logger(logger_name='prompt_result_logger',
                                                         collection_name='promptResultLogs',
                                                         log_level=logging.INFO)

    def __create_logger(self, logger_name, collection_name, log_level):
        logger = logging.getLogger(logger_name)

        logger.setLevel(log_level)

        if not logger.hasHandlers():
            handler = MongoHandler(log_level, self.db_name, collection_name)
            logger.addHandler(handler)

        logger = CustomLoggerAdapter(logger)

        return logger

    # def log_execution_trace(self, message, **kwargs):
    #     self.execution_trace_logger.info(message, extra=kwargs)
    #
    # def log_error(self, message, **kwargs):
    #     self.error_logger.error(message, extra=kwargs)
    #
    # def log_prompt_result(self, message, **kwargs):
    #     self.prompt_result_logger.info(message, extra=kwargs)


mongo_logger = MongoLogger()
execution_trace_logger = mongo_logger.execution_trace_logger
error_logger = mongo_logger.error_logger
prompt_result_logger = mongo_logger.prompt_result_logger
