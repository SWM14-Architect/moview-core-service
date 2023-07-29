from flask import request
from flask_restx import Resource, Namespace

from moview.service import IntervieweeAnswerService, InterviewActionEnum
from moview.service.interviewee_rate.interviewee_answer_score_service import InterviewAnswerScoreService

api = Namespace('answer', description='answer api')


@api.route('/api/interviewee/answer')
class AnswerOfInterviewee(Resource):

    def post(self):
        request_body = request.get_json()

        # IntervieweeDataVO 로드하기 (생성 아님.)
        # load_interview_data_vo()

        # 서비스 호출. (면접관의 다음 행동 결정)
        answer_service = IntervieweeAnswerService()
        vo, next_action = answer_service.determine_next_action_of_interviewer()

        # 다음 행동에 따라 다른 로직 수행
        if next_action == InterviewActionEnum.END_INTERVIEW:
            # 끝났을 경우, 결과 페이지로 이동하라고 프론트에 알려주기 (score_service 호출해야 함)
            score_service = InterviewAnswerScoreService()
            scored_vo = score_service.score_answers_of_interviewee(vo=vo)
            pass
        elif next_action == InterviewActionEnum.NEXT_INITIAL_QUESTION:
            # 다음 초기 질문 출제일 경우, vo에서 다음 초기질문 불러와서 프론트에 보내기
            pass
        elif next_action == InterviewActionEnum.CREATED_FOLLOWUP_QUESTION:
            # 꼬리질문 출제일 경우, vo에서 꼬리질문 불러와서 프론트에 보내기
            pass
        elif next_action == InterviewActionEnum.INAPPROPRIATE_ANSWER:
            # 적절하지 않은 답변일 경우, vo에서 다음 초기질문 불러와서 프론트에 보내기
            pass
        elif next_action == InterviewActionEnum.DIRECT_REQUEST:
            # 재요청일 경우, vo에서 다음 초기질문 불러와서 프론트에 보내기
            pass
