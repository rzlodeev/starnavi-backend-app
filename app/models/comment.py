from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class Comment(Base):
    """Model for comment from user, that belongs to specific post."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    owner = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    def to_dict(self):
        """Represent comment attributes as dict, excluding ones for internal use"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns
                if not c.name.startswith("_")}


class BlockedComment(Base):
    """Model for comment that has been blocked by moderation"""

    __tablename__ = "blocked_comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    blocking_reasoning = Column(Text)

    owner = relationship("User", back_populates="blocked_comments")
    post = relationship("Post", back_populates="blocked_comments")

    def to_dict(self):
        """Represent comment attributes as dict, excluding ones for internal use"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns
                if not c.name.startswith("_")}
