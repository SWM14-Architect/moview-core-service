from pydantic import BaseModel
from datetime import datetime


class OauthUser(BaseModel):
    profile_id: str = None
    profile_nickname: str = None
    profile_image_url: str = None
    thumbnail_image_url: str = None

    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
