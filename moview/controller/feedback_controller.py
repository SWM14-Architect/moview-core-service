from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus
from moview.config.container.container_config import ContainerConfig

api = Namespace('feedback', description='feedback api')


@api.route('/feedback')
class FeedbackConstructor(Resource):

    def post(self):
        session_id = request.cookies.get('session')
        request_body = request.get_json()

        interview_id = request_body['interview_id']
        feedback_list = request_body['feedback_list']

        feedback_service = ContainerConfig().feedback_service

        # todo 로그인 추가 시 session_id를 user_id로 변경해야 함.
        feedback_service.feedback(user_id=session_id, interview_id=interview_id, feedback_list=feedback_list)

        return make_response(jsonify(
            {'message': {
                'interview_id': interview_id
            }}
        ), HTTPStatus.OK)
