from flask import request
from flask_restx import Resource, Namespace

api = Namespace('feedback', description='feedback api')


@api.route('/api/interviewee/feedback')
class FeedbackOfInterviewee(Resource):
    def post(self):
        pass
