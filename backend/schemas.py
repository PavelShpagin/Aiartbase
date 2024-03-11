from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    username: Optional[str]

class UserCreate(UserBase):
    password: Optional[str]

class User(UserCreate):
    id: int
    picture: str
    google_id: Optional[str]
    description: Optional[str]
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
    date: datetime
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

class CategoryCount(BaseModel):
    name: str
    count: int