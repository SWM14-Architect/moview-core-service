import asyncio

from flask import make_response, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.config.container.container_config import ContainerConfig
from moview.config.loggers.mongo_logger import *
from moview.exception.retry_execution_error import RetryExecutionError
from moview.utils.async_controller import async_controller
from moview.decorator.timing_decorator import api_timing_decorator

api = Namespace('evaluation', description='evaluation api')


@api.route('/evaluation')
class EvaluationConstructor(Resource):

    @api_timing_decorator
    @jwt_required()
    @async_controller
    async def post(self):
        user_id = str(get_jwt_identity())
        g.user_id = user_id
        request_body = request.get_json()

        interview_id = request_body['interview_id']
        g.interview_id = interview_id

        evaluation_service = ContainerConfig().evaluation_service

        try:
            results = await evaluation_service.evaluate_answers_of_interviewee(user_id=user_id, interview_id=interview_id)

        except asyncio.exceptions.CancelledError as e:
            error_logger(msg="ASYNCIO CANCELLED ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': 'Oops! 당신의 평가데이터가 우주로 떠나버렸어! 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        except RetryExecutionError as e:
            error_logger(msg="RETRY EXECUTION ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': '앗! 우리 서버에 문제가 발생했네요. 다시 시도해주세요.',
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

        execution_trace_logger("EVALUATION CONTROLLER: POST", results=results)

        return make_response(jsonify(
            {'message':
                 {'evaluations': [{"question_id": question_id, "question": question, "answer": answer, "evaluation": evaluation}
                                  for question_id, question, answer, evaluation in results]
                  }
             }
        ), HTTPStatus.OK)
