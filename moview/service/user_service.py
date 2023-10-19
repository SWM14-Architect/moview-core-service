from flask import g

from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.repository.user.user_repository import UserRepository
from moview.domain.entity.user.user import OauthUser


class UserService(metaclass=SingletonMeta):

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def upsert_user(self, user: dict):
        oauth_user = self.__convert_to_oauth_user(user)
        g.user_id = oauth_user.profile_id
        execution_trace_logger(msg="UPSERT_USER")
        return self.user_repository.upsert_user(oauth_user)

    def get_user(self, profile_id_in_jwt_identity: str) -> dict:
        """

        Args:
            profile_id_in_jwt_identity: jwt identity에 담긴 profile_id

        Returns: 해당 profile_id를 가진 user

        """
        execution_trace_logger(msg="GET_USER")
        found_user = self.user_repository.find_user_by_profile_id_for_jwt(profile_id_in_jwt_identity)

        if found_user:
            return self.__serialize_user(found_user)
        else:
            raise Exception("User not found")

    def __serialize_user(self, user: dict) -> dict:
        return {
            'profile_id': user['profile_id'],
            'profile_nickname': user['profile_nickname'],
            'profile_image_url': user['profile_image_url'],
            'thumbnail_image_url': user['thumbnail_image_url']
        }

    def __convert_to_oauth_user(self, user: dict) -> OauthUser:
        user_info = user['kakao_account']['profile']

        return OauthUser(
            profile_id=user['id'],
            profile_nickname=user_info['nickname'],
            profile_image_url=user_info['profile_image_url'],
            thumbnail_image_url=user_info['thumbnail_image_url'])

    def convert_to_dict(self, user: dict) -> dict[str, str]:
        user_info = user['kakao_account']['profile']
        return {
            "profile_id": user['id'],
            "profile_nickname": user_info['nickname'],
            "profile_image_url": user_info['profile_image_url'],
            "thumbnail_image_url": user_info['thumbnail_image_url']
        }