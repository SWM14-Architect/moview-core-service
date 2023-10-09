from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.exception.stt_error import AudioTooShortError, AudioTooQuietError
from moview.utils.stt import SpeechToText
from moview.utils.timing_decorator import api_timing_decorator
from moview.config.loggers.mongo_logger import *

api = Namespace('stt', description='stt api')


@api.route('/stt')
class STT(Resource):

    @jwt_required()
    @api_timing_decorator
    def post(self):
        try:
            request_body = request.get_json()

            base64_audio_data = request_body['audio_data']
            text = SpeechToText.base64_to_text(base64_audio_data)

            execution_trace_logger("STT CONTROLLER: POST",
                                   base64_audio_data=base64_audio_data,
                                   result_text=text)

            return make_response(jsonify(
                {'message': {
                    'text': text
                }}
            ), HTTPStatus.OK)

        except (AudioTooShortError, AudioTooQuietError) as e:
            execution_trace_logger("STT CONTROLLER: POST (ERROR)",
                                   base64_audio_data=base64_audio_data,
                                   error=str(e))

            return make_response(jsonify(
                {'message': {
                    'error': '음성이 너무 짧거나, 소리가 너무 작아요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.BAD_REQUEST)

        except Exception as e:
            execution_trace_logger("STT CONTROLLER: POST (ERROR)",
                                      base64_audio_data=base64_audio_data,
                                      error=str(e))

            return make_response(jsonify(
                {'message': {
                    'error': '면접관이 혼란스러워하는 것 같아요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)
