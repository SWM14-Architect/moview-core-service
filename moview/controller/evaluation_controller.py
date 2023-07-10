from flask import request
from flask_restx import Resource, Namespace
from moview.modules.analyzer.input_info_analyzer import InputInfoAnalyzer
from moview.modules.analyzer.answer_analyzer import AnswerAnalyzer
from controller import *
from utils.data_manager import *
from http import HTTPStatus

api = Namespace('evaluation', description='evaluation api')


@api.route('/user')
class UserDataUpload(Resource):
    @api.doc("회사이름, 직군, 모집공고, 자기소개서를 입력받습니다.")
    def post(self):
        request_body = request.get_json()
        session["data_manager"] = request_body

        return make_response(
            jsonify({"messages": "success"}),
            HTTPStatus.OK
        )


@api.route('/user/evaluation')
class UserEvaluation(Resource):
    @api.doc("입력받은 사용자 정보를 바탕으로 평가합니다.")
    def get(self):
        chat_manager = ChatManager(streaming=True, temperature=0)

        if check_data_manager():
            return response_data_manager_error()

        data_manager = DataManager()
        data_manager.set_data(session['data_manager'])
        evaluation_manager = EvaluationManager()
        try:
            response = InputInfoAnalyzer(data_manager, evaluation_manager) \
                .analyze_input_info(chat_manager)

        except Exception as e:
            return make_response(
                jsonify({"messages": f"error {e}"}),
                HTTPStatus.REQUEST_TIMEOUT
            )

        session['evaluation_manager'] = evaluation_manager.get_all_evaluation()
        return make_response(
            jsonify({"messages": response}),
            HTTPStatus.OK
        )


@api.route('/answer/evaluation')
class AnswerEvaluation(Resource):
    @api.doc("질문과 답변을 바탕으로 평가합니다.")
    def post(self):
        request_body = request.get_json()
        question_entity = QuestionEntity(request_body['question'], request_body['answer'])

        if check_data_manager():
            return response_data_manager_error()

        if check_evaluation_manager():
            return response_evaluation_manager_error()

        data_manager = DataManager()
        data_manager.set_data(session['data_manager'])
        evaluation_manager = EvaluationManager()
        evaluation_manager.evaluation_records = session['evaluation_manager']

        try:
            response = AnswerAnalyzer(data_manager, question_entity, evaluation_manager) \
                .analyze_answer(ChatManager())

        except Exception as e:
            return make_response(
                jsonify({"messages": f"error {e}"}),
                HTTPStatus.REQUEST_TIMEOUT
            )

        # 평가하면서 추가된 데이터를 세션에 다시 저장합니다.
        session['evaluation_manager'] = evaluation_manager.get_all_evaluation()

        return make_response(
            jsonify({"messages": response}),
            HTTPStatus.OK
        )