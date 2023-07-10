from flask import request
from flask_restx import Resource, Namespace
from moview.modules.question_generator.init_question_generator import InitQuestionGenerator
from moview.modules.question_generator.follow_up_question_generator import FollowUpQuestionGenerator
from utils.data_manager import *
from controller import *
from http import HTTPStatus

api = Namespace('generation', description='generation api')


@api.route('/question')
class InitQuestion(Resource):
    @api.doc("입력받은 사용자 정보를 바탕으로 질문을 생성합니다.")
    def get(self):

        if check_data_manager():
            return response_data_manager_error()

        data_manager = DataManager()
        data_manager.set_data(session['data_manager'])
        chat_manager = ChatManager(temperature=0)
        init_question_generator = InitQuestionGenerator(data_manager)
        try:
            response = init_question_generator.generate_init_question(chat_manager)
        except Exception as e:
            return make_response(
                jsonify({"messages": f"error {e}"}),
                HTTPStatus.REQUEST_TIMEOUT
            )

        return make_response(
            jsonify({"messages": response}),
            HTTPStatus.OK
        )


@api.route('/question/followup')
class FollowUpQuestion(Resource):
    @api.doc("질문과 답변을 바탕으로 심화질문을 생성합니다.")
    def post(self):
        # request_body = request.get_json()

        if check_data_manager():
            return response_data_manager_error()

        if check_evaluation_manager():
            return response_evaluation_manager_error()

        data_manager = DataManager()
        data_manager.set_data(session['data_manager'])
        evaluation_manager = EvaluationManager()
        evaluation_manager.evaluation_records = session['evaluation_manager']

        if not evaluation_manager.evaluation_records.get("answer"):
            return make_response(
                jsonify({"messages": f"최소 질문을 1번 이상 답변하는 과정이 필요합니다."}),
                HTTPStatus.BAD_REQUEST
            )

        follow_up_question_generator = FollowUpQuestionGenerator(data_manager, evaluation_manager)
        try:
            response = follow_up_question_generator.generate_follow_up_question()

        except Exception as e:
            return make_response(
                jsonify({"messages": f"error {e}"}),
                HTTPStatus.REQUEST_TIMEOUT
            )

        return make_response(
            jsonify({"messages": response}),
            HTTPStatus.OK
        )
