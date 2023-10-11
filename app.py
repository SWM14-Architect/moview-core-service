from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from moview.config.jwt.jwt_config import JWTConfig
from flask_jwt_extended import JWTManager

import random
import string

from moview.controller import input_data_controller, answer_controller, evaluation_controller, feedback_controller, \
    light_mode_controller, tts_controller, stt_controller
from moview.controller.oauth import oauth_controller

# Flask App 생성
app = Flask(__name__)

# CORS 설정 - 허용된 Origin만 통신 가능
allowed_origins = [
    "http://localhost:3000",
    "https://test.moview.io",
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


def set_jwt_config():
    """
    Flask App에 JWT 설정 추가
    """
    app.config['JWT_SECRET_KEY'] = JWTConfig.get_jwt_secret_key()
    app.config['JWT_TOKEN_LOCATION'] = JWTConfig.get_jwt_location()
    app.config['JWT_COOKIE_SECURE'] = JWTConfig.get_jwt_cookie_secure()
    app.config['JWT_COOKIE_CSRF_PROTECT'] = JWTConfig.get_jwt_cookie_csrf_protect()
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWTConfig.get_jwt_access_token_expires()
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWTConfig.get_jwt_refresh_token_expires()
    JWTManager(app)


if __name__ == '__main__':
    set_moview_config()
    set_jwt_config()
    app.run(host="0.0.0.0", port=5005, debug=True)
