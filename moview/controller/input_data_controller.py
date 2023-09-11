from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus
from moview.config.container.container_config import ContainerConfig

api = Namespace('input_data', description='input data api')


@api.route('/input')
class InputDataConstructor(Resource):

    def post(self):
        session_id = request.cookies.get('session')
        request_body = request.get_json()

        interviewee_name = request_body['interviewee_name']
        company_name = request_body['company_name']
        job_group = request_body['job_group']
        recruit_announcement = request_body['recruit_announcement']
        cover_letter_questions = request_body['cover_letter_questions']
        cover_letter_answers = request_body['cover_letter_answers']

        interview_service = ContainerConfig().interview_service
        input_data_service = ContainerConfig().input_data_service

        result = input_data_service.ask_initial_question_to_interviewee(
            interviewee_name=interviewee_name,
            company_name=company_name,
            job_group=job_group,
            recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers
        )

        # todo 로그인 추가 시 session_id를 user_id로 변경해야 함.
        interview_document_id = interview_service.create_interview_session(
            session_id=session_id,
            initial_questions=[question for _, question in result['question_document_list']],
        )

        return make_response(jsonify(
            {'message': {
                'initial_questions': [{"question_id": str(object_id), "content": question} for object_id, question in
                                      result['question_document_list']],
                'interview_id': interview_document_id
            }}
        ), HTTPStatus.OK)
