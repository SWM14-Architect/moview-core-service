import inspect
import logging
import sys
import traceback

from moview.config.db.mongo_handler import MongoHandler


class CustomLogRecord(logging.LogRecord):
    """
    CustomLogRecord는 LogRecord 클래스를 상속받아, 클래스명 attribute를 추가한 LogRecord입니다.
    클래스명 이외의 추가 정보들은 extra attribute에 추가됩니다.
    """
    def __init__(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None, **kwargs):
        super().__init__(name, level, fn, lno, msg, args, exc_info, func, sinfo)

        # 클래스명은 record 변수로 추가
        setattr(self, 'classname', kwargs.pop('classname', None))

        # 그 외의 추가 정보는 extra에 추가
        if kwargs:
            if extra is None:
                self.__dict__["extra"] = {}
            self.__dict__["extra"].update(kwargs)


class CustomLogger(logging.getLoggerClass()):
    """
    CustomLogger는 logger의 메소드들을 오버라이드 하여 사용자 정의 로그를 생성합니다.
    """
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def log(self, level, msg, *args, **kwargs):
        """
        logger의 log 메소드를 오버라이드하여, logger에 지정된 레벨과 level 파라미터의 값을 비교하여 로그 생성 가능 여부를 판단하고,
        로그 생성이 가능한 경우, _log 메소드를 호출합니다.
        """
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None, **kwargs):
        """
        logger의 makeRecord 메소드를 오버라이드하여, 기존의 LogRecord 대신 클래스명 attribute가 추가된 CustomLogRecord를 생성해서 리턴합니다.
        """
        return CustomLogRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo, **kwargs)

    def _log(self, level, msg, args, exc_info=None, extra=None, **kwargs):
        """
        logger의 _log 메소드를 오버라이드하여, 로그 생성 시, 클래스명을 추가합니다.
        """
        caller_frame = kwargs.pop('caller_frame', None)

        fn = caller_frame.f_code.co_filename if caller_frame else "(unknown file)"
        lno = caller_frame.f_lineno if caller_frame else 0
        func = caller_frame.f_code.co_name if caller_frame else "(unknown function)"
        kwargs['classname'] = self._get_class_name(caller_frame) if caller_frame else "(unknown class)"
        sinfo = traceback.extract_stack(caller_frame) if caller_frame else None

        if exc_info:
            if not isinstance(exc_info, tuple):
                if isinstance(exc_info, BaseException):
                    exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
                else:
                    exc_info = sys.exc_info()

        record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo, **kwargs)
        self.handle(record)

    @staticmethod
    def _get_class_name(frame):
        """
        주어진 프레임에서 클래스 이름을 추출합니다.
        클래스 메소드가 아니라면 (unknown class)를 리턴합니다.
        """
        args, _, _, value_dict = inspect.getargvalues(frame)

        if len(args) and args[0] == 'self':
            instance = value_dict.get('self', None)

            if instance:
                return instance.__class__.__name__

        return "(unknown class)"


class LoggerWrapper:
    """
    LoggerWrapper는 logger를 wrapping하여, 사용자 정의 로그를 생성합니다.
    """
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, msg=None, *args, **kwargs):
        """
        파이썬의 매직 메소드인 __call__을 이용하여 인스턴스를 함수처럼 호출할 수 있도록 합니다.
        이 때, 자신을 호출한 호출자에 대한 정보를 kwargs에 추가하여 로그 메시지에 포함시킵니다.
        """
        # 자신을 호출한 호출자에 대한 frame을 가져오고, kwargs에 추가
        caller_frame = inspect.currentframe().f_back
        kwargs.update({'caller_frame': caller_frame})

        # 로그 메소드 호출
        self.logger.log(self.logger.level, msg, *args, **kwargs)


class MongoLogger:
    def __init__(self):
        self.db_name = 'log'
        self.execution_trace_logger = LoggerWrapper(self._create_logger(logger_name='execution_trace_logger',
                                                                        collection_name='executionTraceLogs',
                                                                        log_level=logging.INFO))
        self.error_logger = LoggerWrapper(self._create_logger(logger_name='error_logger',
                                                              collection_name='executionTraceLogs',
                                                              log_level=logging.ERROR))
        self.prompt_result_logger = LoggerWrapper(self._create_logger(logger_name='prompt_result_logger',
                                                                      collection_name='executionTraceLogs',
                                                                      log_level=logging.INFO))

    def _create_logger(self, logger_name, collection_name, log_level):
        # 기본 LoggerClass를 저장
        original_logger_class = logging.getLoggerClass()

        logging.setLoggerClass(CustomLogger)
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

        handler = MongoHandler(log_level, self.db_name, collection_name)
        logger.addHandler(handler)

        # LoggerClass 복원
        logging.setLoggerClass(original_logger_class)

        return logger


mongo_logger = MongoLogger()
execution_trace_logger = mongo_logger.execution_trace_logger
error_logger = mongo_logger.error_logger
prompt_result_logger = mongo_logger.prompt_result_logger
