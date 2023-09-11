import requests
from moview.config.oauth.oauth_config import OAuthConfig


class OauthControllerHelper:

    def __init__(self):
        self.auth_server = "https://kauth.kakao.com%s"
        self.api_server = "https://kapi.kakao.com%s"
        self.default_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

    def auth(self, code):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "authorization_code",
                "client_id": OAuthConfig.get_client_id(),
                "client_secret": OAuthConfig.get_client_secret(),
                "redirect_uri": OAuthConfig.get_redirect_uri(),
                "code": code,
            },
        ).json()

    def refresh(self, refresh_token):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "refresh_token",
                "client_id": OAuthConfig.get_client_id(),
                "client_secret": OAuthConfig.get_client_secret(),
                "refresh_token": refresh_token,
            },
        ).json()

    def userinfo(self, bearer_token):
        return requests.post(
            url=self.api_server % "/v2/user/me",
            headers={
                **self.default_header,
                **{"Authorization": bearer_token}
            },
            data={}
        ).json()
