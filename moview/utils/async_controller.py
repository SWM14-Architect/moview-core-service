from functools import wraps
import asyncio


def async_controller(func):
    """
    Controller를 비동기로 실행하기 위한 데코레이터
    Args:
        func: 데코레이터를 적용할 함수

    Returns:
        비동기가 적용된 함수
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapped
