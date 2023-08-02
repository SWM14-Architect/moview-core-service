from flask import session, make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus

api = Namespace('input', description='input api')


@api.route('/interviewee/input')
class InputOfInterviewee(Resource):
    def post(self):
        session_id = request.cookies.get('session')
        return make_response(jsonify({'message': session_id}), HTTPStatus.OK)
