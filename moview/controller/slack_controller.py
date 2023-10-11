from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, Namespace
from http import HTTPStatus
from slack_sdk import WebClient

from moview.config.container.container_config import ContainerConfig
from moview.controller.constants.slack_contants import MAX_USER_CONTENT_LENGTH
from moview.decorator.timing_decorator import api_timing_decorator
from moview.decorator.validation_decorator import validate_char_count
from moview.environment.environment_loader import EnvironmentLoader

api = Namespace('slack', description='slack api')
client = WebClient(token=EnvironmentLoader.getenv('slack-token'))


@api.route('/feedback')
class SlackConstructor(Resource):

    @api_timing_decorator
    @validate_char_count({
        'user_message': MAX_USER_CONTENT_LENGTH,
    })
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        user_service = ContainerConfig().user_service
        user = user_service.get_user(str(user_id))

        request_body = request.get_json()

        user_nickname = user['profile_nickname']
        user_message = request_body['user_message']
        # user_profile = request_body['user_profile']
        created_at = request_body['created_at']

        blocks_message = [
            {
                "type": "section",
                "block_id": "sectionBlockWithRestaurantImageThaiDescription",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{user_nickname}님이 의견을 보냈습니다. {created_at}\n\n *아래는 의견내용입니다:*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "block_id": "sectionBlockWithRestaurantImageThaiA",
                "text": {
                    "type": "mrkdwn",
                    "text": user_message
                },
                # "accessory": {
                #     "type": "image",
                #     "image_url": user_profile,
                #     "alt_text": "profile"
                # }
            },
            {
                "type": "divider"
            }
        ]

        try:
            client.chat_postMessage(
                channel="C0607SQNH5L",
                blocks=blocks_message,
            )
        except Exception as e:
            return make_response(jsonify(
                {'message': {
                    'error': 'Oops! 당신의 글이 우주로 떠나버렸어! 다시 시도해주세요.',
                    'error_message': 'Slack API Error' + str(e)
                }}
            ), HTTPStatus.INTERNAL_SERVER_ERROR)

        return make_response(jsonify(
            {'message': "OK"}
        ), HTTPStatus.OK)
