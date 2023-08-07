from flask import session, make_response, jsonify
from flask_restx import Resource, Namespace
from http import HTTPStatus
from moview.loggers.mongo_logger import *

api = Namespace('session', description='session start api')


@api.route('/interviewee/session')
class SessionOfInterviewee(Resource):
    def post(self):
        session['session_id'] = 'interviewee_session'

        execution_trace_logger("start session", session_id=session['session_id'])

        return make_response(jsonify({'message': session['session_id']}), HTTPStatus.OK)
