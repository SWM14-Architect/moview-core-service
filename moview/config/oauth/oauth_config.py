import os
from enum import Enum


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
        return os.environ.get("KAKAO_CLIENT_ID")

    @staticmethod
    def get_client_secret():
        return os.environ.get("KAKAO_CLIENT_SECRET")

    @staticmethod
    def get_redirect_uri():
        return os.environ.get("KAKAO_REDIRECT_URI")


# OAuth factory
class OAuthConfigFactory:
    @staticmethod
    def get_oauth_config(oauth_provider: OAuthProvider) -> OAuthConfig:
        if oauth_provider == OAuthProvider.KAKAO:
            return KakaoOAuthConfig()
        else:
            raise Exception("Not supported OAuth provider")
