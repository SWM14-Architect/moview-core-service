from flask import request, make_response, jsonify
from flask_restx import Resource, Namespace

from moview.service.interviewee_feedback.interviewee_feedback_service import IntervieweeFeedbackService

api = Namespace('feedback', description='feedback api')


@api.route('/interviewee/feedback')
class FeedbackOfInterviewee(Resource):
    def post(self):
        session_id = request.cookies.get('session')
        request_body = request.get_json()

        feedback_list = request_body['feedbacks']

        # 서비스 호출 (면접자의 피드백 저장)
        feedback_service = IntervieweeFeedbackService()
        feedback_service.save_feedback_of_interviewee(session_id=session_id, feedback_list=feedback_list)

        # 정상적으로 처리되었다는 응답 반환
        return make_response(jsonify({"message": "Feedback successfully saved."}), 200)
