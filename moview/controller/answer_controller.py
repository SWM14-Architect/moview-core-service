from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.config.container.container_config import ContainerConfig
from moview.config.loggers.mongo_logger import *

api = Namespace('answer', description='answer api')


@api.route('/answer')
class AnswerConstructor(Resource):

    @jwt_required()
    def post(self):
        user_id = str(get_jwt_identity())
        request_body = request.get_json()

        interview_id = request_body['interview_id']
        question_id = request_body['question_id']
        question_content = request_body['question_content']
        answer_content = request_body['answer_content']

        answer_service = ContainerConfig().answer_service

        chosen_question, saved_id = answer_service.answer(user_id=user_id, interview_id=interview_id,
                                                          question_id=question_id, question_content=question_content,
                                                          answer_content=answer_content)

        execution_trace_logger("ANSWER CONTROLLER: POST",
                               user_id=user_id,
                               interview_id=interview_id,
                               question_id=question_id,
                               question_content=question_content,
                               answer_content=answer_content,
                               chosen_question=chosen_question,
                               saved_id=saved_id)

        return make_response(jsonify(
            {'message': {
                'question_content': chosen_question,
                'question_id': saved_id
            }}
        ), HTTPStatus.OK)
