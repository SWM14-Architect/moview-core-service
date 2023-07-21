import openai
import datetime
from flask import request
from flask_restx import Resource, Namespace
from moview.modules.analyzer.input_info_analyzer import InputInfoAnalyzer
from moview.modules.analyzer.answer_analyzer import AnswerAnalyzer
from moview.controller import *
from moview.utils.data_manager import *
from moview.utils.util import write_log_in_txt, remove_indent

api = Namespace('evaluation', description='evaluation api')


@api.route('/user')
class UserDataUpload(Resource):
    @api.doc("회사이름, 직군, 모집공고, 자기소개서를 입력받습니다.")
    def post(self):
        # todo : request body 한글로 들어올 경우, 로그에서 한글이 안나옵니다. 추후 문제 해결 필요.
        request_body = request.get_json()
        log = {"time": str(datetime.datetime.now()), "message": "Start of the UserDataUpload",
               "request_body": request_body}
        write_log_in_txt(log, UserDataUpload.__name__)
        session["user_data"] = remove_indent(
            f"""JobAdvertisement At {request_body['user_company']}:
            {request_body['job_requirement']}

            Interviewee`s desired position:
            {request_body['user_job']}

            Interviewee`s coverletter:
            {request_body['cover_letter']}
            """)

        log = {"time": str(datetime.datetime.now()), "message": "End of UserDataUpload"}
        write_log_in_txt(log, UserDataUpload.__name__)

        return make_response(
            jsonify({"messages": "success"}),
            HTTPStatus.OK
        )


@api.route('/user/evaluation')
class UserEvaluation(Resource):
    @api.doc("입력받은 사용자 정보를 바탕으로 평가합니다.")
    def get(self):
        chat_manager = ChatManager(streaming=True, temperature=0)

        log = {"time": str(datetime.datetime.now()), "message": "Start of UserEvaluation"}
        write_log_in_txt(log, UserEvaluation.__name__)

        if is_manager_missing("user_data"):
            log = {"time": str(datetime.datetime.now()), "message": "User Data check failed"}
            write_log_in_txt(log, UserEvaluation.__name__)

            return get_manager_error_response("user_data")

        try:
            response = InputInfoAnalyzer(session['user_data']) \
                .analyze_input_info(chat_manager)
        except openai.OpenAIError as e:

            log = {"time": str(datetime.datetime.now()), "message": f"OpenAIError: {e}"}
            write_log_in_txt(log, UserEvaluation.__name__)

            return make_response(
                jsonify({"messages": f"OpenAI API error\n{e}"}),
                HTTPStatus.REQUEST_TIMEOUT
            )
        except Exception as e:

            log = {"time": str(datetime.datetime.now()), "message": f"Error: {e}"}
            write_log_in_txt(log, UserEvaluation.__name__)

            return make_response(
                jsonify({"messages": f"error {e}"}),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )
        log = {"time": str(datetime.datetime.now()), "message": "End of the UserEvaluation"}
        write_log_in_txt(log, UserEvaluation.__name__)

        session['coverletter_evaluation'] = response

        return make_response(
            jsonify({"messages": response}),
            HTTPStatus.OK
        )


@api.route('/answer/evaluation')
class AnswerEvaluation(Resource):
    @api.doc("질문과 답변을 바탕으로 평가합니다.")
    def post(self):
        request_body = request.get_json()
        question_entity = {
            'question': request_body['question'],
            'answer': request_body['answer']
        }

        log = {"time": str(datetime.datetime.now()), "message": "Start of the AnswerEvaluation",
               "request_body": request_body}
        write_log_in_txt(log, AnswerEvaluation.__name__)

        if is_manager_missing("user_data"):
            log = {"time": str(datetime.datetime.now()), "message": "User Data check failed"}
            write_log_in_txt(log, AnswerEvaluation.__name__)

            return get_manager_error_response("user_data")

        if is_manager_missing("coverletter_evaluation"):
            log = {"time": str(datetime.datetime.now()), "message": "Coverletter Evaluation check failed"}
            write_log_in_txt(log, AnswerEvaluation.__name__)

            return get_manager_error_response("coverletter_evaluation")

        try:
            response = AnswerAnalyzer(session['user_data'], question_entity) \
                .analyze_answer(ChatManager())
        except openai.OpenAIError as e:

            log = {"time": str(datetime.datetime.now()), "message": f"OpenAIError: {e}"}
            write_log_in_txt(log, AnswerEvaluation.__name__)

            return make_response(
                jsonify({"messages": f"OpenAI API error\n{e}"}),
                HTTPStatus.REQUEST_TIMEOUT
            )
        except Exception as e:

            log = {"time": str(datetime.datetime.now()), "message": f"Error: {e}"}
            write_log_in_txt(log, AnswerEvaluation.__name__)

            return make_response(
                jsonify({"messages": f"error {e}"}),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

        # 평가하면서 추가된 데이터를 세션에 다시 저장합니다.
        if not session.get("answer_evaluation"):
            session["answer_evaluation"] = [response]
        else:
            session['answer_evaluation'].append(response)

        return make_response(
            jsonify({"messages": response}),
            HTTPStatus.OK
        )
