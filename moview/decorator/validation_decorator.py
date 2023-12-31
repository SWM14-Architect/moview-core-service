from functools import wraps
from flask import make_response, request, jsonify
from http import HTTPStatus

from moview.config.loggers.mongo_logger import error_logger


def validate_char_count(fields_limits):
    """
    Request Body의 특정 필드의 글자 수를 제한하는 데코레이터입니다.
    Args:
        fields_limits: 글자 수를 제한할 필드와 제한할 글자 수를 key-value로 가지는 딕셔너리

    Returns:
        검증에 실패했을 경우 HTTPStatus.BAD_REQUEST를 반환
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            request_body = request.json
            for field, limit in fields_limits.items():
                if field in request_body and len(request_body[field]) > limit:
                    error_logger("Character count exceeded", field=field, limit=limit, request_body=request_body)
                    return make_response(jsonify(
                        {'error': f'{field} should not exceed {limit} characters'}
                    ), HTTPStatus.BAD_REQUEST)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
