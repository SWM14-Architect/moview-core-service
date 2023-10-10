from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.utils.tts import TextToSpeech
from moview.config.loggers.mongo_logger import *
from moview.decorator.timing_decorator import api_timing_decorator
from moview.decorator.validation_decorator import validate_char_count
from moview.controller.constants.answer_contants import MAX_INTERVIEW_ANSWER_LENGTH

api = Namespace('tts', description='tts api')


@api.route('/tts')
class TTS(Resource):

    @api_timing_decorator
    @validate_char_count({
        'text': MAX_INTERVIEW_ANSWER_LENGTH
    })
    @jwt_required()
    def post(self):
        request_body = request.get_json()

        text = request_body['text']
        try:
            audio_data = TextToSpeech.text_to_base64(text)

        except Exception as e:
            error_logger(msg="UNKNOWN ERROR", error=e)
            return make_response(jsonify(
                {'message': {
                    'error': '면접관이 혼란스러워하는 것 같아요. 다시 시도해주세요.',
                    'error_message': str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        execution_trace_logger("TTS CONTROLLER: POST",
                               text=text,
                               result_audio_data=audio_data)

        return make_response(jsonify(
            {'message': {
                'audio_data': audio_data
            }}
        ), HTTPStatus.OK)