import time
from moview.environment.environment_loader import EnvironmentLoader, EnvironmentEnum
from moview.config.loggers.mongo_logger import execution_trace_logger


# api 호출 시간을 측정하는 데코레이터입니다. 컨트롤러에만 사용바랍니다.
def api_timing_decorator(f):
    def wrap(*args, **kwargs):
        start_time = time.time()
        ret = f(*args, **kwargs)
        end_time = time.time()

        # 첫 번째 인수가 self인지 확인하여 메서드 호출 여부를 확인합니다.
        if args and args[0].__class__:
            class_name = args[0].__class__.__name__
        else:
            class_name = None  # 혹은 클래스가 없는 경우에 대한 기본값을 설정합니다.

        message = f'{class_name}.{f.__name__} function took {str((end_time - start_time) * 1000.0)} ms'

        # 로컬 개발 환경에서는 콘솔에 출력하고, 그 외에는 로그에 기록합니다.
        if EnvironmentLoader.getenv("MOVIEW_CORE_ENV") == "local":
            print(message)
        else:
            execution_trace_logger.info(elapsed=message)

        return ret

    return wrap
