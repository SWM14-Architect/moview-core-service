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
import openai

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
            results = await evaluation_service.evaluate_answers_of_interviewee(user_id=user_id,
                                                                               interview_id=interview_id)

        except RetryExecutionError as e:
            error_logger(msg="RETRY EXECUTION ERROR")
            raise e

        except openai.error.RateLimitError as e:
            error_logger(msg="RATE LIMIT ERROR")
            raise e

        except asyncio.exceptions.CancelledError as e:
            error_logger(msg="ASYNCIO CANCELLED ERROR", error=e)
            raise e

        except Exception as e:
            error_logger(msg="UNKNOWN ERROR", error=e)
            raise e

        execution_trace_logger("EVALUATION CONTROLLER: POST", results=results)

        return make_response(jsonify(
            {'message':
                 {'evaluations': [
                     {"question_id": question_id, "question": question, "answer": answer, "evaluation": evaluation}
                     for question_id, question, answer, evaluation in results]
                  }
             }
        ), HTTPStatus.OK)
