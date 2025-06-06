from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str

class AccountBase(BaseModel):
    id: int
    username: str
    handle: str

    model_config = ConfigDict(from_attributes=True)

class AccountMinimal(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)

class AccountCreate(BaseModel):
    username: str
    handle: str
    email: str
    password: str

class AccountRead(AccountBase):
    email: str
    created_at: datetime
    tweets: List["TweetRead"] # <-- forward reference as a string

class AccountCredentials(BaseModel):
    username: str
    password: str

from backend.schemas.tweet import TweetRead  # <-- "lazy import" to avoid circular referencing
AccountRead.model_rebuild()