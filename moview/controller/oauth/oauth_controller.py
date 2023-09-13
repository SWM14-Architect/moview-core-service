from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from http import HTTPStatus
from flask_jwt_extended import (
    JWTManager, create_access_token,
    get_jwt_identity, jwt_required,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, create_refresh_token
)
from moview.config.container.container_config import ContainerConfig
from moview.controller.oauth.oauth_controller_helper import OauthControllerHelper
from moview.config.oauth.oauth_config import OAuthProvider

api = Namespace('oauth', description='oauth api')


@api.route('/oauth/kakao')
class KakaoOAuthController(Resource):

    def get(self):
        # 1. 전달받은 authorization code 얻어오기
        code = str(request.args.get('code'))

        # 2. accesstoken을 이용해서 kakao 사용자 식별 정보 획득
        oauth = OauthControllerHelper(OAuthProvider.KAKAO)
        auth_info = oauth.auth(code)
        user_dict = oauth.userinfo("Bearer " + auth_info['access_token'])

        # 3. 사용자 정보를 DB에 저장
        user_service = ContainerConfig().user_service
        user_service.upsert_user(user_dict)

        # 4. 사용자 식별 정보를 바탕으로 access token 생성
        response = make_response()
        access_token = create_access_token(identity=user_dict['id'])
        refresh_token = create_refresh_token(identity=user_dict['id'])
        response.set_cookie('ignored', 'true')
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response


@api.route("/userinfo")
@jwt_required()  # 인가 필요할 때 쓰임
class UserInfoController(Resource):
    def get(self):
        # access token 을 이용해 db에서 user 정보를 가져옴
        user_id = get_jwt_identity()

        user_service = ContainerConfig().user_service
        user = user_service.get_user(user_id)

        return jsonify(user)
