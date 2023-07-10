from utils.data_manager import KeyManager
from flask import session, Response, make_response, jsonify
from http import HTTPStatus

# 전역으로 관리하기 위한 객체
key_manager = KeyManager()


def check_manager(manager_name: str) -> bool:
    if not session.get(manager_name):
        return True
    return False


def get_manager_error_response(manager_name: str) -> Response:
    error_messages = {
        "data_manager": "유저 데이터를 먼저 입력해야 합니다.",
        "evaluation_manager": "평가 데이터가 존재하지 않습니다."
    }
    return make_response(
        jsonify({"messages": f"{error_messages[manager_name]}"}),
        HTTPStatus.BAD_REQUEST
    )