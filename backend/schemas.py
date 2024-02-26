from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    hidden: bool
    premium: bool

    class Config:
        from_attributes = True

# Art Schemas
class ArtBase(BaseModel):
    prompt: str

class ArtCreate(ArtBase):
    pass

class Art(ArtBase):
    id: int
    image: str
    premium: bool
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True

# Like Schemas
class LikeBase(BaseModel):
    user_id: int
    art_id: int

    class Config:
        from_attributes = True

# Follow Schemas
class FollowBase(BaseModel):
    follower_id: int
    followee_id: int

    class Config:
        from_attributes = True

# SearchHistory Schemas
class SearchHistoryBase(BaseModel):
    query: str
    date: datetime

class SearchHistoryCreate(SearchHistoryBase):
    pass

class SearchHistory(SearchHistoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# ArtHistory Schemas
class ArtHistoryBase(BaseModel):
    date: datetime

class ArtHistoryCreate(ArtHistoryBase):
    pass

class ArtHistory(ArtHistoryBase):
    id: int
    art_id: int
    user_id: int

    class Config:
        from_attributes = True