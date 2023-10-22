import openai.error
from flask import Flask, jsonify, make_response
from flask_restx import Api
from flask_cors import CORS
from http import HTTPStatus

from moview.config.jwt.jwt_config import JWTConfig
from flask_jwt_extended import JWTManager

import random
import string

from moview.controller import input_data_controller, answer_controller, evaluation_controller, feedback_controller, \
    light_mode_controller, tts_controller, stt_controller, slack_controller
from moview.controller.oauth import oauth_controller
from moview.exception.retry_execution_error import RetryExecutionError

# Flask App 생성
app = Flask(__name__)

# CORS 설정 - 허용된 Origin만 통신 가능
allowed_origins = [
    "https://moview.io",
    "https://test.moview.io",
    "http://localhost:3000"
]
CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

"""This module patches asyncio to allow nested use of `asyncio.run` and `loop.run_until_complete`."""
__import__("nest_asyncio").apply()


def set_moview_config():
    """
    Flask App에 API 추가
    """
    app.secret_key = ''.join(random.choice(string.ascii_letters) for i in range(20))
    api = Api(app)

    app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지

    api.add_namespace(input_data_controller.api, '/interview')
    api.add_namespace(answer_controller.api, '/interview')
    api.add_namespace(evaluation_controller.api, '/interview')
    api.add_namespace(feedback_controller.api, '/interview')
    api.add_namespace(light_mode_controller.api, '/interview')

    # oauth api
    api.add_namespace(oauth_controller.api, '/interview')

    # tts, stt api
    api.add_namespace(tts_controller.api, '/interview')
    api.add_namespace(stt_controller.api, '/interview')

    # slack api
    api.add_namespace(slack_controller.api, '/slack')


def set_jwt_config():
    """
    Flask App에 JWT 설정 추가
    """
    app.config['JWT_SECRET_KEY'] = JWTConfig.get_jwt_secret_key()
    app.config['JWT_TOKEN_LOCATION'] = JWTConfig.get_jwt_location()
    app.config['JWT_COOKIE_SECURE'] = JWTConfig.get_jwt_cookie_secure()
    app.config['JWT_COOKIE_SAMESITE'] = JWTConfig.get_jwt_cookie_samesite()
    app.config['JWT_COOKIE_DOMAIN'] = JWTConfig.get_jwt_cookie_domain()
    app.config['JWT_COOKIE_CSRF_PROTECT'] = JWTConfig.get_jwt_cookie_csrf_protect()
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWTConfig.get_jwt_access_token_expires()
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWTConfig.get_jwt_refresh_token_expires()
    JWTManager(app)


# 아래 에러 핸들러들은 컨트롤러 단에서 exception을 raise할 때 캐치합니다.
@app.errorhandler(RetryExecutionError)
def handle_retry_execution_error(e):
    return make_response(jsonify(
        {'message': {
            'error': 'OpenAI API 호출 중 오류가 발생했어요. 다시 시도해주세요.',
            'error_message': str(e)
        }}
    ), HTTPStatus.SERVICE_UNAVAILABLE)


@app.errorhandler(openai.error.RateLimitError)
def handle_rate_limit_error(e):
    return make_response(jsonify(
        {'message': {
            'error': 'LLM 토큰 1분당 사용량이 초과되었어요. 1분 뒤에 다시 시도해주세요~ :)',
            'error_message': str(e)
        }}
    ), HTTPStatus.SERVICE_UNAVAILABLE)


@app.errorhandler(Exception)
def handle_exception(e):
    return make_response(jsonify(
        {'message': {
            'error': '오잉? 이상한 오류 메시지가 나타났어요. 다시 시도해주세요.',
            'error_message': str(e)
        }}
    ), HTTPStatus.INTERNAL_SERVER_ERROR)


set_moview_config()
set_jwt_config()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)
