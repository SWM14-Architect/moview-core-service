from moview.environment.environment_loader import EnvironmentLoader, EnvironmentEnum


class JWTConfig:
    @staticmethod
    def get_jwt_secret_key():
        return EnvironmentLoader.getenv("jwt-secret-key")

    @staticmethod
    def get_jwt_location():
        return ["cookies"]

    @staticmethod
    def get_jwt_cookie_secure():
        if EnvironmentLoader.get_local_env("MOVIEW_CORE_ENV") in [EnvironmentEnum.PRODUCTION.value,
                                                                  EnvironmentEnum.DEVELOPMENT.value]:
            return True
        else:
            return False

    @staticmethod
    def get_jwt_cookie_csrf_protect():
        return True

    @staticmethod
    def get_jwt_cookie_samesite():
        if EnvironmentLoader.get_local_env("MOVIEW_CORE_ENV") in [EnvironmentEnum.PRODUCTION.value,
                                                                  EnvironmentEnum.DEVELOPMENT.value]:
            return "None"
        else:
            return None

    @staticmethod
    def get_jwt_cookie_domain():
        if EnvironmentLoader.get_local_env("MOVIEW_CORE_ENV") in [EnvironmentEnum.PRODUCTION.value,
                                                                  EnvironmentEnum.DEVELOPMENT.value]:
            return ".moview.io"
        else:
            return None

    @staticmethod
    def get_jwt_access_token_expires():
        return 1800  # 30 minutes

    @staticmethod
    def get_jwt_refresh_token_expires():
        return 604800  # 1 week
