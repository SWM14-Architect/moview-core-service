from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from typing import List, Tuple

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

        execution_trace_logger("start answer", request_body=request_body, session_id=session_id)

        question = request_body['question']
        answer = request_body['answer']

        # 서비스 호출 (면접관의 다음 행동 결정)
        answer_service = IntervieweeAnswerService()
        next_question, next_action = answer_service.determine_next_action_of_interviewer(session_id=session_id,
                                                                                         question=question,
                                                                                         answer=answer)

        # 다음 행동에 따라 다른 로직 수행
        if next_action == InterviewerActionEnum.END_INTERVIEW:
            # 끝났을 경우, 면접자 답변 평가 서비스를 호출하여 점수와 분석 내용을 불러옴
            evaluation_service = InterviewAnswerEvaluationService()
            
            interviewee_answer_evaluations = evaluation_service.evaluate_answers_of_interviewee(session_id=session_id)
            
            formatted_evaluations = AnswerOfInterviewee._format_evaluations(interviewee_answer_evaluations)

            execution_trace_logger("end_interview", next_question=next_question, next_action=next_action.value)
            
            return make_response(jsonify({'message': {
                'content': formatted_evaluations,
                'flag': str(next_action)
            }}), HTTPStatus.OK)
        else:
            execution_trace_logger("next_question", next_question=next_question, next_action=next_action.value)

            return make_response(jsonify({'message': {
                'content': next_question,
                'flag': str(next_action)
            }}), HTTPStatus.OK)

    @staticmethod
    def _format_evaluations(evaluations) -> List[Tuple[str, str, str, str, str]]:
        return list(zip(
            evaluations.question_list,
            evaluations.answer_list,
            evaluations.category_and_sub_category_list,
            evaluations.score_of_answer_list,
            evaluations.analysis_of_answer_list,
        ))
