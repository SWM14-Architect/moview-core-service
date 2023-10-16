from flask import make_response, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.config.container.container_config import ContainerConfig
from moview.config.loggers.mongo_logger import *
from moview.exception.initial_question_parse_error import InitialQuestionParseError
from moview.exception.retry_execution_error import RetryExecutionError
from moview.utils.async_controller import async_controller
from moview.decorator.timing_decorator import api_timing_decorator
from moview.decorator.validation_decorator import validate_char_count
from moview.controller.constants.input_data_constants import (MAX_COMPANY_NAME_LENGTH, MAX_POSITION_NAME_LENGTH,
                                                              MAX_RECRUITMENT_LENGTH, MAX_COVERLETTER_QUESTION_LENGTH,
                                                              MAX_COVERLETTER_ANSWER_LENGTH)

import asyncio

api = Namespace('input_data', description='input data api')


@api.route('/input')
class InputDataConstructor(Resource):

    @api_timing_decorator
    @validate_char_count({
        'company_name': MAX_COMPANY_NAME_LENGTH,
        'job_group': MAX_POSITION_NAME_LENGTH,
        'recruit_announcement': MAX_RECRUITMENT_LENGTH,
        'cover_letter_questions': MAX_COVERLETTER_QUESTION_LENGTH,
        'cover_letter_answers': MAX_COVERLETTER_ANSWER_LENGTH
    })
    @jwt_required()
    @async_controller
    async def post(self):
        user_id = str(get_jwt_identity())
        g.user_id = user_id
        request_body = request.get_json()

        interviewee_name = request_body['interviewee_name']
        company_name = request_body['company_name']
        job_group = request_body['job_group']
        recruit_announcement = request_body['recruit_announcement']
        cover_letter_questions = request_body['cover_letter_questions']
        cover_letter_answers = request_body['cover_letter_answers']

        interview_service = ContainerConfig().interview_service
        input_data_service = ContainerConfig().input_data_service

        # 1. Interview Document 생성
        try:
            interview_document_id = interview_service.create_interview(
                user_id=user_id,
            )
            g.interview_id = interview_document_id

        except Exception as e:
            error_logger(msg="CREATE INTERVIEW DOCUMENT ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': '오잉? 이상한 오류 메시지가 나타났어요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)
        
        # 2. Initial Question 생성
        try:
            result = await input_data_service.ask_initial_question_to_interviewee(
                interviewee_name=interviewee_name,
                company_name=company_name,
                job_group=job_group,
                recruit_announcement=recruit_announcement,
                cover_letter_questions=cover_letter_questions,
                cover_letter_answers=cover_letter_answers
            )

        except asyncio.exceptions.CancelledError as e:
            error_logger(msg="ASYNCIO CANCELLED ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': 'Oops! 당신의 질문이 우주로 떠나버렸어! 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        except InitialQuestionParseError as e:
            error_logger(msg="INITIAL QUESTION PARSE ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': '"뭐라고요? 그건 아마도 우주적 수준의 질문이었나봐요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        except RetryExecutionError as e:
            error_logger(msg="RETRY EXECUTION ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': '앗! 특이한 질문을 찾아내었습니다. 하지만 제 지식 범위를 넘어선 것 같아요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        except Exception as e:
            error_logger(msg="UNKNOWN ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': '면접관이 혼란스러워하는 것 같아요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        # 3. Interview Document에 Initial Input Data Document ID 업데이트
        try:
            interview_service.update_interview_with_initial_input_data(
                user_id=user_id,
                interview_document_id=interview_document_id,
                input_data_document_id=result['input_data_document']
            )

        except Exception as e:
            error_logger(msg="CREATE INTERVIEW DOCUMENT ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': '오잉? 이상한 오류 메시지가 나타났어요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        execution_trace_logger("INPUT DATA CONTROLLER: POST",
                               interviewee_name=interviewee_name,
                               company_name=company_name,
                               job_group=job_group,
                               recruit_announcement=recruit_announcement,
                               cover_letter_questions=cover_letter_questions,
                               cover_letter_answers=cover_letter_answers)

        return make_response(jsonify(
            {'message': {
                'initial_questions': [{"question_id": str(object_id), "content": question} for object_id, question in
                                      result['question_document_list']],
                'interview_id': interview_document_id
            }}
        ), HTTPStatus.OK)
