from functools import wraps
from flask import make_response, request, jsonify
from http import HTTPStatus

from moview.config.loggers.mongo_logger import error_logger


def validate_char_count(fields_limits):
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
