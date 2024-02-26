from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    description = Column(String)
    username = Column(String)
    hidden = Column(Boolean, default=False)
    premium = Column(Boolean, default=False)

    arts = relationship("Art", back_populates="owner")
    likes = relationship("Like", back_populates="user")
    followers = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete-orphan")
    following = relationship("Follow", foreign_keys="Follow.followee_id", back_populates="followee", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user")
    art_history = relationship("ArtHistory", back_populates="user")

class Art(Base):
    __tablename__ = "arts"
    
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String)
    prompt = Column(String)
    premium = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="arts")
    likes = relationship("Like", back_populates="art")
    art_history = relationship("ArtHistory", back_populates="art")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String)
    date = Column(DateTime)

    user = relationship("User", back_populates="search_history")

class ArtHistory(Base):
    __tablename__ = "art_history"

    id = Column(Integer, primary_key=True, index=True)
    art_id = Column(Integer, ForeignKey("arts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)

    user = relationship("User", back_populates="art_history")
    art = relationship("Art", back_populates="art_history")

class Like(Base):
    __tablename__ = "likes"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    art_id = Column(Integer, ForeignKey("arts.id"), primary_key=True)

    user = relationship("User", back_populates="likes")
    art = relationship("Art", back_populates="likes")

class Follow(Base):
    __tablename__ = "follows"
    
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    followee_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    follower = relationship("User", foreign_keys=[follower_id], back_populates="followers")
    followee = relationship("User", foreign_keys=[followee_id], back_populates="following")