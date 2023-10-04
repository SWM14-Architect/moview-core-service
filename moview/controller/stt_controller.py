from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.exception.stt_error import AudioTooShortError, AudioTooQuietError
from moview.utils.stt import SpeechToText

api = Namespace('stt', description='stt api')


@api.route('/stt')
class STT(Resource):
    def post(self):
        try:
            # todo: api 남용 못하도록 jwt 토큰으로 인증 추가
            request_body = request.get_json()

            base64_audio_data = request_body['audio_data']
            text = SpeechToText.base64_to_text(base64_audio_data)

            return make_response(jsonify(
                {'message': {
                    'text': text
                }}
            ), HTTPStatus.OK)

        except (AudioTooShortError, AudioTooQuietError) as e:
            return make_response(jsonify(
                {'message': {
                    'error': str(e)
                }}
            ), HTTPStatus.BAD_REQUEST)
