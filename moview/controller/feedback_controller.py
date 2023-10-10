from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.config.container.container_config import ContainerConfig
from moview.config.loggers.mongo_logger import *
from moview.decorator.timing_decorator import api_timing_decorator

api = Namespace('feedback', description='feedback api')


@api.route('/feedback')
class FeedbackConstructor(Resource):

    @jwt_required()
    @api_timing_decorator
    def post(self):
        user_id = str(get_jwt_identity())
        request_body = request.get_json()

        interview_id = request_body['interview_id']
        question_ids = request_body['question_ids']
        feedback_scores = request_body['feedback_scores']

        feedback_service = ContainerConfig().feedback_service

        try:
            feedback_service.feedback(user_id=user_id, interview_id=interview_id, question_ids=question_ids,
                                      feedback_scores=feedback_scores)

        except Exception as e:
            error_logger(msg="UNKNOWN ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': '면접관이 혼란스러워하는 것 같아요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        execution_trace_logger("FEEDBACK CONTROLLER: POST",
                               user_id=user_id,
                               interview_id=interview_id,
                               question_ids=question_ids,
                               feedback_scores=feedback_scores)

        return make_response(jsonify(
            {'message': {
                'interview_id': interview_id
            }}
        ), HTTPStatus.OK)
