import openai
import datetime
from flask_restx import Resource, Namespace
from moview.modules.question_generator.init_question_generator import InitQuestionGenerator
from moview.modules.question_generator.follow_up_question_generator import FollowUpQuestionGenerator
from moview.utils.data_manager import *
from moview.controller import *
from moview.utils.util import write_log_in_txt

api = Namespace('generation', description='generation api')


@api.route('/question')
class InitQuestion(Resource):
    @api.doc("입력받은 사용자 정보를 바탕으로 질문을 생성합니다.")
    def get(self):

        log = {"time": str(datetime.datetime.now()), "message": "Start of InitQuestion"}
        write_log_in_txt(log, InitQuestion.__name__)

        if check_manager("data_manager"):
            log = {"time": str(datetime.datetime.now()), "message": "Data manager check failed"}
            write_log_in_txt(log, InitQuestion.__name__)
            return get_manager_error_response("data_manager")

        data_manager = DataManager()
        data_manager.set_data(session['data_manager'])
        chat_manager = ChatManager(temperature=0)
        init_question_generator = InitQuestionGenerator(data_manager)
        try:
            response = init_question_generator.generate_init_question(chat_manager)
        except openai.OpenAIError as e:

            log = {"time": str(datetime.datetime.now()), "message": f"OpenAIError: {e}"}
            write_log_in_txt(log, InitQuestion.__name__)

            return make_response(
                jsonify({"messages": f"OpenAI API error\n{e}"}),
                HTTPStatus.REQUEST_TIMEOUT
            )
        except Exception as e:

            log = {"time": str(datetime.datetime.now()), "message": f"Error: {e}"}
            write_log_in_txt(log, InitQuestion.__name__)

            return make_response(
                jsonify({"messages": f"error {e}"}),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

        log = {"time": str(datetime.datetime.now()), "message": "End of the InitQuestion"}
        write_log_in_txt(log, InitQuestion.__name__)

        return make_response(
            jsonify({"messages": response}),
            HTTPStatus.OK
        )


@api.route('/question/followup')
class FollowUpQuestion(Resource):
    @api.doc("질문과 답변을 바탕으로 심화질문을 생성합니다.")
    def post(self):

        log = {"time": str(datetime.datetime.now()), "message": "Start of FollowUpQuestion"}
        write_log_in_txt(log, FollowUpQuestion.__name__)

        if check_manager("data_manager"):
            log = {"time": str(datetime.datetime.now()), "message": "Data manager check failed"}
            write_log_in_txt(log, FollowUpQuestion.__name__)

            return get_manager_error_response("data_manager")

        if check_manager("evaluation_manager"):
            log = {"time": str(datetime.datetime.now()), "message": "Evaluation manager check failed"}
            write_log_in_txt(log, FollowUpQuestion.__name__)

            return get_manager_error_response("evaluation_manager")

        data_manager = DataManager()
        data_manager.set_data(session['data_manager'])
        evaluation_manager = EvaluationManager()
        evaluation_manager.evaluation_records = session['evaluation_manager']

        if not evaluation_manager.evaluation_records.get("answer"):
            log = {"time": str(datetime.datetime.now()), "message": "Evaluation manager answer record not exist"}
            write_log_in_txt(log, FollowUpQuestion.__name__)

            return make_response(
                jsonify({"messages": f"질문을 답변하는 과정이 최소 1회 이상 필요합니다."}),
                HTTPStatus.BAD_REQUEST
            )

        follow_up_question_generator = FollowUpQuestionGenerator(
            data_manager,
            evaluation_manager
        )

        try:
            response = follow_up_question_generator \
                .generate_follow_up_question()
        except openai.OpenAIError as e:

            log = {"time": str(datetime.datetime.now()), "message": f"OpenAIError: {e}"}
            write_log_in_txt(log, FollowUpQuestion.__name__)

            return make_response(
                jsonify({"messages": f"OpenAI API error\n{e}"}),
                HTTPStatus.REQUEST_TIMEOUT
            )
        except Exception as e:

            log = {"time": str(datetime.datetime.now()), "message": f"Error: {e}"}
            write_log_in_txt(log, FollowUpQuestion.__name__)

            return make_response(
                jsonify({"messages": f"error {e}"}),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

        log = {"time": str(datetime.datetime.now()), "message": "End of the FollowUpQuestion"}
        write_log_in_txt(log, FollowUpQuestion.__name__)

        return make_response(
            jsonify({"messages": response}),
            HTTPStatus.OK
        )
