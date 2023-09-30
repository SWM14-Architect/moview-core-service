from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.config.container.container_config import ContainerConfig
from moview.config.loggers.mongo_logger import *

api = Namespace('light_mode', description='light mode api')


@api.route('/light')
class LightModeConstructor(Resource):

    @jwt_required()
    def post(self):
        user_id = str(get_jwt_identity())

        request_body = request.get_json()

        interviewee_name = request_body['interviewee_name']
        company_name = request_body['company_name']
        job_group = request_body['job_group']
        keyword = request_body['keyword']

        interview_service = ContainerConfig().interview_service
        light_mode_service = ContainerConfig().light_mode_service

        result = light_mode_service.ask_light_question_to_interviewee(
            interviewee_name=interviewee_name,
            company_name=company_name,
            job_group=job_group, keyword=keyword)

        # Parse Error 발생했을 경우 500 에러 반환
        if result is None:
            return make_response(jsonify(
                {'message': {
                    'light_questions': None,
                    'interview_id': None
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        interview_document_id = interview_service.create_interview(
            user_id=user_id,
            input_data_document_id=result['input_data_document']
        )

        execution_trace_logger("LIGHT MODE CONTROLLER: POST",
                               user_id=user_id,
                               interviewee_name=interviewee_name,
                               company_name=company_name,
                               job_group=job_group,
                               keyword=keyword,
                               interview_document_id=interview_document_id)

        return make_response(jsonify(
            {'message': {
                'light_questions': [{"question_id": str(object_id), "content": question} for object_id, question in
                                    result['question_document_list']],
                'interview_id': interview_document_id
            }}
        ), HTTPStatus.OK)
