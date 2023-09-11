from pydantic import BaseModel
from datetime import datetime


class OauthUser(BaseModel):
    oauth_profile: str = None

    oauth_id: str = None
    oauth_nickname: str = None
    oauth_profile_image_url: str = None
    oauth_thumbnail_image_url: str = None

    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
