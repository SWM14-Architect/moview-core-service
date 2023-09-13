from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus
from moview.config.container.container_config import ContainerConfig
from moview.utils.async_controller import async_controller

api = Namespace('evaluation', description='evaluation api')


@api.route('/evaluation')
class EvaluationConstructor(Resource):

    @async_controller
    async def post(self):
        session_id = request.cookies.get('session')
        request_body = request.get_json()

        interview_id = request_body['interview_id']

        evaluation_service = ContainerConfig().evaluation_service

        # todo 로그인 추가 시 session_id를 user_id로 변경해야 함.
        results = await evaluation_service.evaluate_answer_of_interviewee(user_id=session_id, interview_id=interview_id)
        print(results)

        return make_response(jsonify(
            {'message':
                 {'evaluations': [{"question": question, "answer": answer, "evaluation": evaluation}
                                  for question, answer, evaluation in results]
                  }
             }
        ), HTTPStatus.OK)
