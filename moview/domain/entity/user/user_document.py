from pydantic import BaseModel, Field
from datetime import datetime


class OauthUser(BaseModel):
    profile_id: str = None
    profile_nickname: str = None
    profile_image_url: str = None
    thumbnail_image_url: str = None

    created_at: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
