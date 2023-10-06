import os
from enum import Enum

from moview.environment.environment_loader import EnvironmentLoader


# Oauth 제공자 Enum
class OAuthProvider(Enum):
    KAKAO = 1
    GOOGLE = 2
    FACEBOOK = 3
    GITHUB = 4


# OAuth 설정을 위한 인터페이스 (나중에 구글, 페이스북 등 다른 OAuth 서비스를 사용할 때 확장성을 위해)
class OAuthConfig:

    @staticmethod
    def get_client_id():
        pass

    @staticmethod
    def get_client_secret():
        pass

    @staticmethod
    def get_redirect_uri():
        pass


# 카카오 OAuth 설정을 위한 구체 클래스
class KakaoOAuthConfig(OAuthConfig):
    @staticmethod
    def get_client_id():
        # 앱키
        return EnvironmentLoader.getenv("kakao-client-id")

    @staticmethod
    def get_client_secret():
        # Secret Key
        return EnvironmentLoader.getenv("kakao-client-secret")

    @staticmethod
    def get_redirect_uri():
        return EnvironmentLoader.getenv("kakao-redirect-uri")


# OAuth factory
class OAuthConfigFactory:
    @staticmethod
    def get_oauth_config(oauth_provider: OAuthProvider) -> OAuthConfig:
        if oauth_provider == OAuthProvider.KAKAO:
            return KakaoOAuthConfig()
        else:
            raise Exception("Not supported OAuth provider")
