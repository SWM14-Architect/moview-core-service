from flask import make_response, jsonify, request
from flask_restx import Resource, Namespace
from flask_jwt_extended import (create_access_token,
                                get_jwt_identity, jwt_required,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies, create_refresh_token
                                )
from moview.config.container.container_config import ContainerConfig
from moview.controller.oauth.oauth_controller_helper import OauthControllerHelper
from moview.config.oauth.oauth_config import OAuthProvider
from moview.config.oauth.oauth_config import OAuthConfigFactory

api = Namespace('oauth', description='oauth api')


@api.route('/oauth')
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
        response.set_cookie('logined', 'true')
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response


@api.route("/userinfo")
class UserInfoController(Resource):
    @jwt_required()  # 인가 필요할 때 쓰임
    def get(self):
        # access token 을 이용해 db에서 user 정보를 가져옴
        user_id = get_jwt_identity()

        user_service = ContainerConfig().user_service
        user = user_service.get_user(str(user_id))

        return jsonify(user)


@api.route('/oauth/url')
class KakaoOAuthURLController(Resource):

    def get(self):
        """
        Kakao OAuth URL 가져오기
        """
        client_id = OAuthConfigFactory.get_oauth_config(OAuthProvider.KAKAO).get_client_id()
        redirect_uri = OAuthConfigFactory.get_oauth_config(OAuthProvider.KAKAO).get_redirect_uri()

        return jsonify(
            kakao_oauth_url="https://kauth.kakao.com/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code" \
                            % (client_id, redirect_uri))


@api.route("/oauth/refresh")
class OAuthRefreshController(Resource):

    def post(self):
        #     refresh token을 인자로 받은 후,
        #     kakao에서 access_token 및 refresh_token을 재발급.
        refresh_token = request.get_json()['refresh_token']
        result = OauthControllerHelper.refresh(refresh_token)
        return jsonify(result)


@api.route("/oauth/userinfo")
class OAuthUserInfoController(Resource):

    def post(self):
        #     access token을 인자로 받은 후,
        #     kakao에서 user 정보를 가져옴.
        access_token = request.args.get('access_token')
        oauth_helper = OauthControllerHelper(OAuthProvider.KAKAO)
        result = oauth_helper.userinfo(bearer_token="Bearer " + access_token)
        return jsonify(result)


@api.route('/token/refresh')
class TokenRefreshController(Resource):

    @jwt_required(refresh=True)
    def post(self):
        # refresh token을 이용해 access token 재발급
        current_user_id = get_jwt_identity()
        response = jsonify({'result': True})
        access_token = create_access_token(identity=current_user_id)
        set_access_cookies(response, access_token)
        return response


@api.route('/token/remove')
class TokenRemoveController(Resource):

    def post(self):
        # refresh token을 이용해 access token 재발급
        response = jsonify({'result': True})
        unset_jwt_cookies(response)
        response.delete_cookie('logined')
        return response
