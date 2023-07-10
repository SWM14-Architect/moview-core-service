from utils.data_manager import KeyManager
from flask import session, Response, make_response, jsonify
from http import HTTPStatus

# 전역으로 관리하기 위한 객체
key_manager = KeyManager()


def check_data_manager() -> bool:
    if not session.get('data_manager'):
        return True
    return False


def response_data_manager_error() -> Response:
    return make_response(
        jsonify({"messages": f"유저 데이터를 먼저 입력해야 합니다."}),
        HTTPStatus.BAD_REQUEST
    )


def check_evaluation_manager() -> bool:
    if session.get('evaluation_manager') is None:
        return True
    return False


def response_evaluation_manager_error() -> Response:
    return make_response(
        jsonify({"messages": f"평가 데이터가 존재하지 않습니다."}),
        HTTPStatus.BAD_REQUEST
    )