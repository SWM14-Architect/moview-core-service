from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.config.container.container_config import ContainerConfig
from moview.config.loggers.mongo_logger import *
from moview.utils.async_controller import async_controller

api = Namespace('input_data', description='input data api')


@api.route('/input')
class InputDataConstructor(Resource):

    @jwt_required()
    @async_controller
    async def post(self):
        user_id = str(get_jwt_identity())
        request_body = request.get_json()

        interviewee_name = request_body['interviewee_name']
        company_name = request_body['company_name']
        job_group = request_body['job_group']
        recruit_announcement = request_body['recruit_announcement']
        cover_letter_questions = request_body['cover_letter_questions']
        cover_letter_answers = request_body['cover_letter_answers']

        interview_service = ContainerConfig().interview_service
        input_data_service = ContainerConfig().input_data_service

        result = await input_data_service.ask_initial_question_to_interviewee(
            interviewee_name=interviewee_name,
            company_name=company_name,
            job_group=job_group,
            recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers
        )

        interview_document_id = interview_service.create_interview(
            user_id=user_id,
            input_data_document_id=result['input_data_document'],
            initial_questions=[question for _, question in result['question_document_list']],
        )

        execution_trace_logger("INPUT DATA CONTROLLER: POST",
                               user_id=user_id,
                               interviewee_name=interviewee_name,
                               company_name=company_name,
                               job_group=job_group,
                               recruit_announcement=recruit_announcement,
                               cover_letter_questions=cover_letter_questions,
                               cover_letter_answers=cover_letter_answers,
                               interview_document_id=interview_document_id)

        return make_response(jsonify(
            {'message': {
                'initial_questions': [{"question_id": str(object_id), "content": question} for object_id, question in
                                      result['question_document_list']],
                'interview_id': interview_document_id
            }}
        ), HTTPStatus.OK)
