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
        results[0] = (results[0][0], results[0][1], results[0][2], [
            "장점 분석\n면접 지원자는 SW 마에스트로 프로젝트와 팀프로젝트에서 협업을 위해 다양한 도구와 기술을 사용했다고 설명했습니다. 지라를 사용하여 개발 일정을 관리하고, 컴플런스와 노션을 이용하여 문서를 관리하고 산출물을 정리했다고 언급했습니다. 또한 슬랙을 통해 빠르게 문제 이슈나 개발 현황을 공유하여 접근성을 높였다고 말했습니다. 마지막으로 Git과 GitHub를 사용하여 코드 형상 관리와 코드 리뷰를 통해 협업 능력을 향상시켰다고 설명했습니다. 이러한 다양한 도구와 기술을 사용하여 효과적인 협업을 진행한 것은 면접 지원자의 긍정적인 점입니다.",
            "단점 분석\n면접 지원자의 답변은 어떤 도구와 기술을 사용했는지에 대한 설명은 제공했지만, 실제로 어떤 역할을 맡았고 어떤 결과를 도출했는지에 대한 구체적인 내용은 언급되지 않았습니다. 면접 지원자는 프로젝트에서 어떤 도전과제를 경험했고, 어떻게 해결했는지에 대한 내용도 더 추가할 필요가 있습니다. 또한, 면접 지원자는 협업을 통해 어떤 가치를 창출했는지에 대한 설명도 부족합니다. 간단한 예시나 구체적인 성과를 언급하여 협업으로 어떤 결과를 이끌어냈는지를 더 구체적으로 설명하는 것이 개선이 필요한 부분입니다."])
        return make_response(jsonify(
            {'message':
                 {'evaluations': [
                     {"question_id": question_id, "question": question, "answer": answer, "evaluation": evaluation}
                     for question_id, question, answer, evaluation in results]
                  }
             }
        ), HTTPStatus.OK)
