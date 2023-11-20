from flask import make_response, jsonify
from flask_restx import Resource, Namespace
from http import HTTPStatus


api = Namespace('health', description='health api')


@api.route('health')
class HealthChecker(Resource):

    def get(self):
        return make_response(jsonify({'message': 'health check ok'}), HTTPStatus.OK)
