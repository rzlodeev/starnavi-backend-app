from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    profile = relationship("UserProfile", backref="user")

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="owner")


class UserProfile(Base):
    """User model for user info that will be shown"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bio = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
