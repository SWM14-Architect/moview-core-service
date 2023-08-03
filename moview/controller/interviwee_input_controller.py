from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus
from moview.service.interviewee_input.interviewee_input_service import IntervieweeInputService

api = Namespace('input', description='input api')


@api.route('/interviewee/input')
class InputOfInterviewee(Resource):

    def post(self):
        session_id = request.cookies.get('session')
        request_body = request.get_json()

        interviewee_name = request_body['interviewee_name']
        job_group = request_body['job_group']
        recruit_announcement = request_body['recruit_announcement']
        cover_letter_questions = request_body['cover_letter_questions']
        cover_letter_answers = request_body['cover_letter_answers']

        input_service = IntervieweeInputService()

        first_question = input_service.ask_initial_question_to_interviewee(
            session_id=session_id, interviewee_name=interviewee_name, job_group=job_group,
            recruit_announcement=recruit_announcement, cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers
        )

        # todo dto로 리스폰스 바꾸기
        return make_response(jsonify({'message': first_question}), HTTPStatus.OK)
