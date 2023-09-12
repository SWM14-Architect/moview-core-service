import os


class JWTConfig:
    @staticmethod
    def get_jwt_secret_key():
        return os.getenv("JWT_SECRET_KEY")

    @staticmethod
    def get_jwt_location():
        return ["cookies"]

    @staticmethod
    def get_jwt_cookie_secure():
        return False

    @staticmethod
    def get_jwt_cookie_csrf_protect():
        return True

    @staticmethod
    def get_jwt_access_token_expires():
        return 300  # 5 minutes

    @staticmethod
    def get_jwt_refresh_token_expires():
        return 604800  # 1 week
