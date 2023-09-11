from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.repository.user.user_repository import UserRepository
from moview.domain.entity.user.user import OauthUser


class UserService(metaclass=SingletonMeta):

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def upsert_user(self, user: dict):
        oauth_user = self.__convert_to_oauth_user(user)
        execution_trace_logger(msg="UPSERT_USER", user_profile_id=oauth_user.profile_id)
        self.user_repository.upsert_user(oauth_user)

    def __convert_to_oauth_user(self, user: dict) -> OauthUser:
        user_info = user['kakao_account']['profile']

        return OauthUser(
            profile_id=user['id'],
            profile_nickname=user_info['nickname'],
            profile_image_url=user_info['profile_image_url'],
            thumbnail_image_url=user_info['thumbnail_image_url'])
