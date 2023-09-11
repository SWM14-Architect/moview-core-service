import os


class OAuthConfig:

    @staticmethod
    def get_client_id():
        return os.environ.get("CLIENT_ID")

    @staticmethod
    def get_client_secret():
        return os.environ.get("CLIENT_SECRET")

    @staticmethod
    def get_redirect_uri():
        return os.environ.get("REDIRECT_URI")
