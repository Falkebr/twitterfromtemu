from pydantic import BaseModel, ConfigDict
from typing import List

class SearchRequest(BaseModel):
    query: str

class HashtagBase(BaseModel):
    tag: str

class HashtagCreate(HashtagBase):
    pass

class HashtagRead(HashtagBase):
    id: int
    tag: str

    model_config = ConfigDict(from_attributes=True)