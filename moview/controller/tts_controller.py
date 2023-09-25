from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus

from moview.utils.tts import TextToSpeech

api = Namespace('tts', description='tts api')


@api.route('/tts')
class TTS(Resource):
    def post(self):
        # todo: api 남용 못하도록 jwt 토큰으로 인증 추가
        request_body = request.get_json()

        text = request_body['text']
        audio_data = TextToSpeech.text_to_base64(text)

        return make_response(jsonify(
            {'message': {
                'audio_data': audio_data
            }}
        ), HTTPStatus.OK)
