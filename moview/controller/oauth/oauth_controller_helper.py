import requests
from moview.config.oauth.oauth_config import OAuthConfigFactory, OAuthProvider


class OauthControllerHelper:

    def __init__(self, oauth_provider: OAuthProvider):
        self.oauth_provider = oauth_provider
        self.auth_server = self.__get_auth_server()
        self.api_server = self.__get_api_server()
        self.default_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

    def __get_auth_server(self):
        if self.oauth_provider == OAuthProvider.KAKAO:
            return "https://kauth.kakao.com%s"
        else:
            raise Exception("Not supported OAuth provider")

    def __get_api_server(self):
        if self.oauth_provider == OAuthProvider.KAKAO:
            return "https://kapi.kakao.com%s"
        else:
            raise Exception("Not supported OAuth provider")

    def auth(self, code):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "authorization_code",
                "client_id": OAuthConfigFactory.get_oauth_config(self.oauth_provider).get_client_id(),
                "client_secret": OAuthConfigFactory.get_oauth_config(self.oauth_provider).get_client_secret(),
                "redirect_uri": OAuthConfigFactory.get_oauth_config(self.oauth_provider).get_redirect_uri(),
                "code": code,
            },
        ).json()

    def refresh(self, refresh_token):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "refresh_token",
                "client_id": OAuthConfigFactory.get_oauth_config(self.oauth_provider).get_client_id(),
                "client_secret": OAuthConfigFactory.get_oauth_config(self.oauth_provider).get_client_secret(),
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
