from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus
from moview.service.interviewee_answer.interviewee_answer_service import IntervieweeAnswerService
from moview.service.interviewee_rate.interviewee_answer_score_service import InterviewAnswerScoreService
from moview.service.interviewee_answer.interviewer_action_enum import InterviewerActionEnum
from moview.service.interviewee_rate.interviewee_answer_score_service import InterviewAnswerScoreService

api = Namespace('answer', description='answer api')


@api.route('/interviewee/answer')
class AnswerOfInterviewee(Resource):

    def post(self):
        session_id = request.cookies.get('session')
        request_body = request.get_json()

        question = request_body['question']
        answer = request_body['answer']

        # 서비스 호출. (면접관의 다음 행동 결정)
        answer_service = IntervieweeAnswerService()
        next_question, next_action = answer_service.determine_next_action_of_interviewer(session_id=session_id,
                                                                                         question=question,
                                                                                         answer=answer)

        # 다음 행동에 따라 다른 로직 수행
        if next_action == InterviewerActionEnum.END_INTERVIEW:
            # 끝났을 경우, 결과 페이지로 이동하라고 프론트에 알려주기 (score_service 호출해야 함)
            score_service = InterviewAnswerScoreService()
            # todo score_service 호출해야 함

            return make_response(jsonify({'message': {
                'content': [],  # todo score_service에서 평가한 리스트가 들어가야 함.
                'flag': str(next_action)
            }}), HTTPStatus.OK)
        else:
            return make_response(jsonify({'message': {
                'content': next_question,
                'flag': str(next_action)
            }}), HTTPStatus.OK)
