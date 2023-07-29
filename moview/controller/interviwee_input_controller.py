from flask import request
from flask_restx import Resource, Namespace

api = Namespace('input', description='input api')


@api.route('/api/interviewee/input')
class InputOfInterviewee(Resource):
    def post(self):
        pass
