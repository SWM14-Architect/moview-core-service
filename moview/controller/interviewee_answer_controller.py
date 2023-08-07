from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace

from http import HTTPStatus
from moview.service.interviewee_answer.interviewee_answer_service import IntervieweeAnswerService
from moview.service.interviewee_answer.interviewer_action_enum import InterviewerActionEnum
from moview.service.interviewee_evaluation.interviewee_answer_evaluation_service import InterviewAnswerEvaluationService
from moview.loggers.mongo_logger import *

api = Namespace('answer', description='answer api')


@api.route('/interviewee/answer')
class AnswerOfInterviewee(Resource):

    def post(self):
        session_id = request.cookies.get('session')
        request_body = request.get_json()

        execution_trace_logger("start answer", args1=request_body, args2=session_id)

        question = request_body['question']
        answer = request_body['answer']

        # 서비스 호출. (면접관의 다음 행동 결정)
        answer_service = IntervieweeAnswerService()
        next_question, next_action = answer_service.determine_next_action_of_interviewer(session_id=session_id,
                                                                                         question=question,
                                                                                         answer=answer)

        # 다음 행동에 따라 다른 로직 수행
        if next_action == InterviewerActionEnum.END_INTERVIEW:
            evaluation_service = InterviewAnswerEvaluationService()

            execution_trace_logger("end_interview", args1=next_question, args2=next_action)

            return make_response(jsonify({'message': {
                'content': [],  # todo score_service에서 평가한 리스트가 들어가야 함.
                'flag': str(next_action)
            }}), HTTPStatus.OK)
        else:
            execution_trace_logger("next_question", args1=next_question, args2=next_action)

            return make_response(jsonify({'message': {
                'content': next_question,
                'flag': str(next_action)
            }}), HTTPStatus.OK)
