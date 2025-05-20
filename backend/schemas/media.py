from pydantic import BaseModel, ConfigDict

class MediaBase(BaseModel):
    media_type: str

class MediaCreate(MediaBase):
    url: str

class MediaRead(MediaBase):
    id: int
    tweet_id: int

    model_config = ConfigDict(from_attributes=True)