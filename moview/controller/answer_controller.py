from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus
from moview.config.container.container_config import ContainerConfig

api = Namespace('answer', description='answer api')


@api.route('/answer')
class AnswerConstructor(Resource):

    def post(self):
        session_id = request.cookies.get('session')
        request_body = request.get_json()

        interview_id = request_body['interview_id']
        question_id = request_body['question_id']
        question_content = request_body['question_content']
        answer_content = request_body['answer_content']

        answer_service = ContainerConfig().answer_service

        # todo 로그인 추가 시 session_id를 user_id로 변경해야 함.
        chosen_question, saved_id = answer_service.answer(user_id=session_id, interview_id=interview_id,
                                                          question_id=question_id, question_content=question_content,
                                                          answer_content=answer_content)

        return make_response(jsonify(
            {'message': {
                'question_content': chosen_question,
                'question_id': saved_id
            }}
        ), HTTPStatus.OK)
